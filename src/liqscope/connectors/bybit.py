"""Conector para Bybit Linear implementando DataSource con aiohttp."""

import asyncio
import contextlib
import json
import logging
import random
from datetime import UTC, datetime
from typing import Any

import aiohttp
from pydantic import ValidationError

from liqscope.config import Settings, get_settings
from liqscope.connectors.base import ConnectionStatus, DataSource
from liqscope.models.common import DataCoverage, DataOrigin, Exchange, PositionSide
from liqscope.models.liquidation import LiquidationEvent

logger = logging.getLogger("liqscope.connectors.bybit")


class BybitConnector(DataSource):
    """Conector para streams de mercado de Bybit Linear (V5 WebSocket).

    Implementa:
    1. allLiquidation: Stream de todas las liquidaciones públicas ejecutadas en Bybit.
       URL Oficial: https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation
       Push frequency: 500ms
       Topic: allLiquidation.{symbol}
    """

    def __init__(
        self,
        symbol: str = "BTCUSDT",
        settings: Settings | None = None,
        queue: asyncio.Queue[LiquidationEvent] | None = None,
    ) -> None:
        super().__init__(exchange=Exchange.BYBIT)
        self.symbol = symbol.upper()
        self.settings = settings or get_settings()
        self._queue: asyncio.Queue[LiquidationEvent] = queue or asyncio.Queue()

        self._running: bool = False
        self._had_disconnect: bool = False
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None

    @property
    def queue(self) -> asyncio.Queue[LiquidationEvent]:
        """Cola asíncrona controlada para recepción ordenada de eventos."""
        return self._queue

    @property
    def has_disconnection_gap(self) -> bool:
        """Indica si ha ocurrido una desconexión en la sesión actual."""
        return self._had_disconnect

    def mark_disconnect(self) -> None:
        """Registra un corte de conexión o gap en la sesión."""
        self._had_disconnect = True

    def reset_disconnect(self) -> None:
        """Restablece el estado de continuidad de la sesión."""
        self._had_disconnect = False

    @classmethod
    def parse_all_liquidation(
        cls,
        payload: dict[str, Any],
        incomplete: bool = False,
    ) -> list[LiquidationEvent]:
        """Parsea y valida un mensaje crudo de allLiquidation contra el esquema Pydantic.

        URL Oficial: https://bybit-exchange.github.io/docs/v5/websocket/public/all-liquidation
        Esquema oficial:
          'topic': str (ej: 'allLiquidation.ROSEUSDT')
          'type': str ('snapshot')
          'ts': int (timestamp del sistema en ms)
          'data': list[dict]
            'T': int (The updated timestamp en ms)
            's': str (Symbol name, ej: 'ROSEUSDT')
            'S': str ("Position side. Buy, Sell. When you receive a Buy update,
                      this means that a long position has been liquidated")
            'v': str (Executed size)
            'p': str (Bankruptcy price)
        """
        topic = str(payload.get("topic", ""))
        if not topic.startswith("allLiquidation."):
            logger.warning(
                "Tópico no reconocido para allLiquidation descartado",
                extra={"topic": topic},
            )
            return []

        raw_data = payload.get("data")
        if not isinstance(raw_data, list):
            logger.warning(
                "Payload de allLiquidation sin array de datos válido",
                extra={"payload": payload},
            )
            return []

        events: list[LiquidationEvent] = []
        system_ts = payload.get("ts")

        for item in raw_data:
            if not isinstance(item, dict):
                continue
            try:
                symbol = str(item["s"]).upper()
                raw_side = str(item["S"]).strip().title()

                # Cita literal de Bybit:
                # "Position side. Buy, Sell. When you receive a Buy update,
                # this means that a long position has been liquidated"
                if raw_side == "Buy":
                    side = PositionSide.LONG
                elif raw_side == "Sell":
                    side = PositionSide.SHORT
                else:
                    logger.warning(
                        "Lado de posición desconocido en allLiquidation",
                        extra={"raw_side": raw_side, "item": item},
                    )
                    continue

                # 'p' es el Bankruptcy Price reportado por Bybit. No se asigna a price.
                bankruptcy_price = float(item["p"])
                quantity = float(item["v"])
                filled_quantity = quantity
                usd_volume = bankruptcy_price * quantity

                time_ms = int(item.get("T", system_ts if system_ts is not None else 0))
                timestamp = datetime.fromtimestamp(time_ms / 1000.0, tz=UTC)

                event = LiquidationEvent(
                    exchange=Exchange.BYBIT,
                    symbol=symbol,
                    side=side,
                    price=None,
                    bankruptcy_price=bankruptcy_price,
                    quantity=quantity,
                    filled_quantity=filled_quantity,
                    usd_volume=usd_volume,
                    timestamp=timestamp,
                    origin=DataOrigin.OBSERVED,
                    coverage=DataCoverage.COMPLETE,
                    incomplete=incomplete,
                )
                events.append(event)
            except (KeyError, ValueError, TypeError, ValidationError) as exc:
                logger.warning(
                    "Item de allLiquidation inválido descartado",
                    extra={"error": str(exc), "item": item},
                )
                continue

        return events

    async def handle_raw_message(self, raw_data: str | bytes) -> list[LiquidationEvent]:
        """Decodifica el mensaje entrante y emite los eventos correspondientes."""
        try:
            payload = json.loads(raw_data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Error al deserializar JSON de Bybit", extra={"error": str(exc)})
            return []

        if not isinstance(payload, dict):
            return []

        topic = payload.get("topic", "")
        if isinstance(topic, str) and topic.startswith("allLiquidation."):
            events = self.parse_all_liquidation(payload, incomplete=self._had_disconnect)
            for event in events:
                await self.emit_liquidation(event)
                await self._queue.put(event)
            return events

        # Confirmación de suscripción o ping/pong
        op = payload.get("op")
        if op in ("subscribe", "ping", "pong"):
            logger.debug("Mensaje operativo recibido de Bybit", extra={"payload": payload})

        return []

    async def start(self) -> None:
        """Inicia el bucle de conexión WebSocket con reconexión exponencial y jitter."""
        if self._running:
            logger.warning("El conector de Bybit ya está en ejecución")
            return

        self._running = True
        self._task = asyncio.create_task(self._connection_loop(), name="bybit-ws-loop")

    async def stop(self) -> None:
        """Detiene de forma limpia la conexión y las tareas activas."""
        logger.info("Deteniendo conector Bybit...")
        self._running = False

        if self._task and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

        if self._ws and not self._ws.closed:
            await self._ws.close()
            self._ws = None

        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

        self._status = ConnectionStatus.DISCONNECTED
        logger.info("Conector Bybit detenido exitosamente")

    async def _connection_loop(self) -> None:
        """Bucle principal con reconexión automática resiliente."""
        delay = self.settings.ws_reconnect_min_delay_sec

        while self._running:
            try:
                self._status = ConnectionStatus.CONNECTING
                ws_url = self.settings.bybit_ws_url
                logger.info("Conectando a Bybit WebSocket: %s", ws_url)

                async with aiohttp.ClientSession() as session:
                    self._session = session
                    async with session.ws_connect(ws_url) as ws:
                        self._ws = ws
                        self._status = ConnectionStatus.CONNECTED
                        delay = self.settings.ws_reconnect_min_delay_sec
                        logger.info("Conexión establecida con Bybit WebSocket")

                        # Enviar suscripción a allLiquidation
                        sub_payload = {
                            "op": "subscribe",
                            "args": [f"allLiquidation.{self.symbol}"],
                        }
                        await ws.send_str(json.dumps(sub_payload))
                        logger.info("Suscripción enviada a allLiquidation.%s", self.symbol)

                        async for msg in ws:
                            if not self._running:
                                break
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                await self.handle_raw_message(msg.data)
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                logger.warning("WebSocket cerrado o error: %s", msg.type)
                                self._had_disconnect = True
                                break

            except asyncio.CancelledError:
                logger.debug("Bucle de Bybit cancelado para apagado")
                break
            except Exception as exc:
                self._status = ConnectionStatus.ERROR
                self._had_disconnect = True
                logger.error("Error imprevisto en la conexión de Bybit: %s", exc)

            if not self._running:
                break

            self._status = ConnectionStatus.RECONNECTING
            self._had_disconnect = True
            jitter = delay * self.settings.ws_reconnect_jitter * (2 * random.random() - 1)
            actual_delay = max(0.1, delay + jitter)
            logger.info("Reconectando a Bybit en %.2f segundos...", actual_delay)

            try:
                await asyncio.sleep(actual_delay)
            except asyncio.CancelledError:
                break

            delay = min(delay * 2.0, self.settings.ws_reconnect_max_delay_sec)

        self._status = ConnectionStatus.DISCONNECTED
