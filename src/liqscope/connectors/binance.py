"""Conector para Binance Futures (USDT-M) implementando DataSource con aiohttp."""

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
from liqscope.models.common import DataOrigin, Exchange, PositionSide
from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import Trade

logger = logging.getLogger("liqscope.connectors.binance")


class BinanceFuturesConnector(DataSource):
    """Conector oficial para streams de mercado de Binance Futures (USDⓈ-M).

    Implementa:
    1. aggTrade: Stream de trades agregados en tiempo real.
       URL Oficial: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams
    2. forceOrder: Stream de órdenes forzadas de liquidación (ritmo 1000ms).
       URL Oficial: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams
    """

    def __init__(
        self,
        symbol: str = "btcusdt",
        settings: Settings | None = None,
    ) -> None:
        super().__init__(exchange=Exchange.BINANCE)
        self.symbol = symbol.lower()
        self.settings = settings or get_settings()

        self._running: bool = False
        self._session: aiohttp.ClientSession | None = None
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._task: asyncio.Task[None] | None = None

    @classmethod
    def parse_agg_trade(cls, payload: dict[str, Any]) -> Trade | None:
        """Parsea y valida un mensaje crudo de aggTrade contra el esquema Pydantic.

        URL Oficial: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams
        Campos oficiales:
          's': symbol (str, ej: 'BTCUSDT')
          'p': price (str)
          'q': quantity (str)
          'T': trade time (int ms)
          'm': isBuyerMaker (bool). Si es True, el comprador es maker (venta agresiva -> SHORT).
          'a': aggregate trade ID (int)
        """
        try:
            symbol = str(payload["s"]).upper()
            price = float(payload["p"])
            quantity = float(payload["q"])
            is_buyer_maker = bool(payload["m"])
            side = PositionSide.SHORT if is_buyer_maker else PositionSide.LONG
            trade_time_ms = int(payload["T"])
            timestamp = datetime.fromtimestamp(trade_time_ms / 1000.0, tz=UTC)
            trade_id = payload.get("a")

            return Trade(
                exchange=Exchange.BINANCE,
                symbol=symbol,
                price=price,
                quantity=quantity,
                side=side,
                timestamp=timestamp,
                trade_id=str(trade_id) if trade_id is not None else None,
            )
        except (KeyError, ValueError, TypeError, ValidationError) as exc:
            logger.warning(
                "Mensaje aggTrade inválido descartado",
                extra={"error": str(exc), "payload": payload},
            )
            return None

    @classmethod
    def parse_force_order(cls, payload: dict[str, Any]) -> LiquidationEvent | None:
        """Parsea y valida un mensaje crudo de forceOrder contra el esquema Pydantic.

        URL Oficial: https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams
        Estructura oficial:
          'o': {
            's': symbol (str)
            'S': side ('SELL' = long liquidado; 'BUY' = short liquidado)
            'p': price (str)
            'q': original quantity (str)
            'z': accumulated filled quantity (str)
            'T': order trade time (int ms)
          }
        """
        try:
            order = payload["o"]
            symbol = str(order["s"]).upper()
            raw_side = str(order["S"]).upper()
            # Si la orden forzada de cierre es SELL, se liquidó una posición LONG
            # Si la orden forzada de cierre es BUY, se liquidó una posición SHORT
            side = PositionSide.LONG if raw_side == "SELL" else PositionSide.SHORT

            price = float(order["p"])
            quantity = float(order["q"])
            filled_qty = float(order.get("z", order.get("l", quantity)))
            usd_volume = price * quantity
            trade_time_ms = int(order["T"])
            timestamp = datetime.fromtimestamp(trade_time_ms / 1000.0, tz=UTC)

            return LiquidationEvent(
                exchange=Exchange.BINANCE,
                symbol=symbol,
                side=side,
                price=price,
                quantity=quantity,
                filled_quantity=filled_qty,
                usd_volume=usd_volume,
                timestamp=timestamp,
                origin=DataOrigin.ESTIMATED,
            )
        except (KeyError, ValueError, TypeError, ValidationError) as exc:
            logger.warning(
                "Mensaje forceOrder inválido descartado",
                extra={"error": str(exc), "payload": payload},
            )
            return None

    async def handle_raw_message(self, raw_data: str | bytes) -> None:
        """Decodifica el mensaje entrante y lo despacha según su tipo."""
        try:
            payload = json.loads(raw_data)
        except (json.JSONDecodeError, TypeError) as exc:
            logger.warning("Error al deserializar JSON de Binance", extra={"error": str(exc)})
            return

        if not isinstance(payload, dict):
            return

        # Binance puede enviar streams combinados {"stream": "...", "data": {...}}
        data = payload.get("data", payload)
        event_type = data.get("e")

        if event_type == "aggTrade":
            trade = self.parse_agg_trade(data)
            if trade is not None:
                await self.emit_trade(trade)
        elif event_type == "forceOrder":
            liquidation = self.parse_force_order(data)
            if liquidation is not None:
                await self.emit_liquidation(liquidation)

    def _get_stream_url(self) -> str:
        """Construye la URL del WebSocket con los streams requeridos."""
        # Multi-stream: <symbol>@aggTrade y <symbol>@forceOrder
        base_url = self.settings.binance_ws_url.rstrip("/")
        # URL oficial para streams combinados
        return f"{base_url}/stream?streams={self.symbol}@aggTrade/{self.symbol}@forceOrder"

    async def start(self) -> None:
        """Inicia la tarea en segundo plano para conexión y reconexión."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def stop(self) -> None:
        """Detiene la conexión y cierra la sesión aiohttp limpiamente."""
        self._running = False
        if self._ws and not self._ws.closed:
            await self._ws.close()
        if self._session and not self._session.closed:
            await self._session.close()
        if self._task and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        self._status = ConnectionStatus.DISCONNECTED

    async def _run_loop(self) -> None:
        """Bucle principal con reconexión exponencial y jitter."""
        min_delay = self.settings.ws_reconnect_min_delay_sec
        max_delay = self.settings.ws_reconnect_max_delay_sec
        jitter_factor = self.settings.ws_reconnect_jitter
        current_delay = min_delay

        timeout = aiohttp.ClientTimeout(total=self.settings.http_request_timeout_sec)
        self._session = aiohttp.ClientSession(timeout=timeout)

        while self._running:
            self._status = ConnectionStatus.CONNECTING
            url = self._get_stream_url()
            try:
                logger.info("Conectando a WebSocket de Binance", extra={"url": url})
                async with self._session.ws_connect(url) as ws:
                    self._ws = ws
                    self._status = ConnectionStatus.CONNECTED
                    current_delay = min_delay  # Reset tras conexión exitosa
                    logger.info("Conexión establecida con Binance Futures")

                    async for msg in ws:
                        if not self._running:
                            break
                        if msg.type in (aiohttp.WSMsgType.TEXT, aiohttp.WSMsgType.BINARY):
                            await self.handle_raw_message(msg.data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED):
                            logger.warning("Cierre de WebSocket recibido de Binance")
                            break
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(
                                "Error en WebSocket de Binance",
                                extra={"ws_error": str(ws.exception())},
                            )
                            break
            except (TimeoutError, aiohttp.ClientError, OSError) as exc:
                self._status = ConnectionStatus.RECONNECTING
                logger.warning(
                    "Conexión con Binance perdida o fallida. Reintentando...",
                    extra={"error": str(exc), "retry_in_sec": current_delay},
                )
            except Exception as exc:
                self._status = ConnectionStatus.ERROR
                logger.exception(
                    "Error imprevisto en el conector de Binance", extra={"error": str(exc)}
                )

            if self._running:
                self._status = ConnectionStatus.RECONNECTING
                # Backoff exponencial con jitter
                jitter = current_delay * jitter_factor * (random.random() * 2 - 1)
                sleep_time = max(min_delay, min(max_delay, current_delay + jitter))
                await asyncio.sleep(sleep_time)
                current_delay = min(max_delay, current_delay * 2)

        self._status = ConnectionStatus.DISCONNECTED
