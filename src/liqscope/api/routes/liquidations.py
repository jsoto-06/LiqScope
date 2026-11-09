"""Rutas de API y WebSocket para el stream de liquidaciones forzadas en tiempo real."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from liqscope.models.liquidation import LiquidationEvent, LiquidationStats
from liqscope.services.liquidation_feed import get_liquidation_feed_service

router = APIRouter(prefix="/liquidations", tags=["Liquidations Real-Time"])


@router.get(
    "/recent",
    summary="Historial reciente de liquidaciones en memoria",
    description="Retorna los últimos eventos de liquidación forzada capturados por el feed.",
)
async def get_recent_liquidations(
    symbol: str = Query(default="ALL", description="Símbolo para filtrar (ej. BTCUSDT o ALL)"),
    min_usd: float = Query(default=0.0, ge=0.0, description="Volumen mínimo nocional en USD"),
    limit: int = Query(default=50, ge=1, le=200, description="Cantidad máxima de eventos"),
) -> dict[str, Any]:
    """Consulta los eventos de liquidación recientes almacenados en el búfer."""
    feed = get_liquidation_feed_service()
    events = feed.get_recent(symbol=symbol, min_usd=min_usd, limit=limit)
    stats = feed.get_stats()
    return {
        "status": "ok",
        "symbol": symbol.upper(),
        "count": len(events),
        "events": [e.model_dump() for e in events],
        "stats": stats.model_dump(),
        "is_feed_running": feed.is_running,
    }


@router.get(
    "/stats",
    response_model=LiquidationStats,
    summary="Estadísticas de la sesión de liquidaciones",
)
async def get_liquidation_stats() -> LiquidationStats:
    """Retorna las métricas acumuladas de la sesión actual."""
    feed = get_liquidation_feed_service()
    return feed.get_stats()


@router.websocket("/ws")
async def websocket_liquidation_stream(websocket: WebSocket) -> None:
    """Canal WebSocket bidireccional para recibir eventos de liquidación en directo."""
    await websocket.accept()
    feed = get_liquidation_feed_service()
    queue = feed.subscribe()

    try:
        # Enviar estado inicial de conexión
        await websocket.send_json({
            "type": "connected",
            "message": "Conectado al feed en directo de LiqScope REKT Ticker",
            "stats": feed.get_stats().model_dump(),
        })

        while True:
            # Esperar el próximo evento con timeout para enviar ping/keepalive
            try:
                event = await asyncio.wait_for(queue.get(), timeout=25.0)
                await websocket.send_json({
                    "type": "liquidation",
                    "data": event.model_dump(),
                })
            except asyncio.TimeoutError:
                # Keepalive ping
                await websocket.send_json({"type": "ping"})
    except (WebSocketDisconnect, ConnectionResetError):
        pass
    except Exception:
        pass
    finally:
        feed.unsubscribe(queue)
