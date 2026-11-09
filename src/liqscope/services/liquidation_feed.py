"""Servicio en segundo plano para el streaming y almacenamiento en memoria de liquidaciones forzadas reales."""

from __future__ import annotations

import asyncio
from collections import deque
import logging
from typing import Any

import aiohttp

from liqscope.models.liquidation import LiquidationEvent, LiquidationStats

logger = logging.getLogger("liqscope.services.liquidation_feed")

BINANCE_WS_URL = "wss://fstream.binance.com/market/ws/!forceOrder@arr"


class LiquidationFeedService:
    """Consumidor del stream de liquidaciones en vivo de Binance con distribución a clientes."""

    def __init__(self, max_buffer_size: int = 200) -> None:
        self.max_buffer_size = max_buffer_size
        self._events: deque[LiquidationEvent] = deque(maxlen=max_buffer_size)
        self._listeners: set[asyncio.Queue[LiquidationEvent]] = set()
        self._stats = LiquidationStats()
        self._task: asyncio.Task[None] | None = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """Indica si el servicio de streaming está activo."""
        return self._running and self._task is not None and not self._task.done()

    def start(self) -> None:
        """Inicia la tarea en segundo plano que escucha el stream WebSocket."""
        if self.is_running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(), name="liquidation_feed_ws")
        logger.info("LiquidationFeedService iniciado.")

    async def stop(self) -> None:
        """Detiene la tarea de consumo y limpia los escuchas."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        self._listeners.clear()
        logger.info("LiquidationFeedService detenido.")

    def subscribe(self) -> asyncio.Queue[LiquidationEvent]:
        """Registra una nueva cola de eventos para un cliente WebSocket conectado."""
        queue: asyncio.Queue[LiquidationEvent] = asyncio.Queue(maxsize=100)
        self._listeners.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[LiquidationEvent]) -> None:
        """Elimina una cola de eventos al desconectarse el cliente."""
        self._listeners.discard(queue)

    def get_recent(
        self,
        symbol: str | None = None,
        min_usd: float = 0.0,
        limit: int = 50,
    ) -> list[LiquidationEvent]:
        """Retorna una lista filtrada de los eventos más recientes en el buffer."""
        result: list[LiquidationEvent] = []
        target_sym = symbol.upper().strip() if symbol and symbol.upper() != "ALL" else None

        for ev in reversed(self._events):
            if target_sym and ev.symbol != target_sym:
                continue
            if ev.volume_usd < min_usd:
                continue
            result.append(ev)
            if len(result) >= limit:
                break
        return result

    def get_stats(self) -> LiquidationStats:
        """Retorna las estadísticas acumuladas de la sesión."""
        return self._stats

    async def _run_loop(self) -> None:
        """Bucle continuo de conexión y reconexión con backoff."""
        backoff_sec = 2.0
        while self._running:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(
                        BINANCE_WS_URL,
                        heartbeat=20.0,
                        timeout=aiohttp.ClientTimeout(total=15.0),
                    ) as ws:
                        logger.info("Conectado con éxito a Binance forceOrder WebSocket.")
                        backoff_sec = 2.0  # Reset backoff tras conexión exitosa

                        async for msg in ws:
                            if not self._running:
                                break
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                try:
                                    payload = msg.json()
                                    self._process_message(payload)
                                except Exception as parse_err:
                                    logger.debug("Error procesando mensaje de liquidación: %s", parse_err)
                            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                logger.warning("WebSocket de liquidaciones cerrado por el servidor.")
                                break
            except asyncio.CancelledError:
                break
            except Exception as err:
                logger.warning("Fallo en la conexión del stream de liquidaciones (%s). Reconectando en %.1fs...", err, backoff_sec)
                await asyncio.sleep(backoff_sec)
                backoff_sec = min(backoff_sec * 1.5, 30.0)

    def _process_message(self, data: dict[str, Any]) -> None:
        """Parsea el mensaje JSON de Binance y lo distribuye a los escuchas."""
        if not isinstance(data, dict):
            return

        order = data.get("o")
        if not order:
            return

        sym = order.get("s", "")
        side = order.get("S", "SELL")
        liq_side = "LONG" if side == "SELL" else "SHORT"

        try:
            qty = float(order.get("q", 0.0))
            p = float(order.get("p", 0.0))
            ap = float(order.get("ap", 0.0))
            exec_p = ap if ap > 0 else p
            volume_usd = qty * exec_p
            ts = int(order.get("T", data.get("E", 0)))
        except (ValueError, TypeError):
            return

        if exec_p <= 0 or volume_usd <= 0:
            return

        is_whale = volume_usd >= 100_000.0
        is_mega_whale = volume_usd >= 500_000.0

        event = LiquidationEvent(
            symbol=sym,
            side=side,
            liquidated_side=liq_side,
            price=p if p > 0 else exec_p,
            avg_price=exec_p,
            quantity=qty,
            volume_usd=volume_usd,
            timestamp=ts,
            is_whale=is_whale,
            is_mega_whale=is_mega_whale,
            exchange="binance",
        )

        self._events.append(event)
        self._update_stats(event)

        # Difusión a clientes WebSocket activos
        stale_queues: list[asyncio.Queue[LiquidationEvent]] = []
        for q in self._listeners:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                stale_queues.append(q)

        for sq in stale_queues:
            self._listeners.discard(sq)

    def _update_stats(self, event: LiquidationEvent) -> None:
        """Actualiza las estadísticas acumuladas en tiempo de ejecución."""
        s = self._stats
        new_count = s.total_count + 1
        new_vol = s.total_volume_usd + event.volume_usd
        new_long_count = s.long_count + (1 if event.liquidated_side == "LONG" else 0)
        new_long_vol = s.long_volume_usd + (event.volume_usd if event.liquidated_side == "LONG" else 0.0)
        new_short_count = s.short_count + (1 if event.liquidated_side == "SHORT" else 0)
        new_short_vol = s.short_volume_usd + (event.volume_usd if event.liquidated_side == "SHORT" else 0.0)
        new_whale_count = s.whale_count + (1 if event.is_whale else 0)

        largest = s.largest_event
        if largest is None or event.volume_usd > largest.volume_usd:
            largest = event

        self._stats = LiquidationStats(
            total_count=new_count,
            total_volume_usd=new_vol,
            long_count=new_long_count,
            long_volume_usd=new_long_vol,
            short_count=new_short_count,
            short_volume_usd=new_short_vol,
            whale_count=new_whale_count,
            largest_event=largest,
        )


_global_feed_service: LiquidationFeedService | None = None


def get_liquidation_feed_service() -> LiquidationFeedService:
    """Proveedor singleton del servicio de feed de liquidaciones."""
    global _global_feed_service
    if _global_feed_service is None:
        _global_feed_service = LiquidationFeedService()
    return _global_feed_service
