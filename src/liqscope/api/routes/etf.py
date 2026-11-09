"""Rutas de API para el Tracker Institucional de ETFs Spot (Bitcoin & Ethereum)."""

from __future__ import annotations

from fastapi import APIRouter, Query

from liqscope.models.etf import DailyInflowRecord, ETFSnapshot, ETFTrackerResponse
from liqscope.services.etf_service import get_etf_service

router = APIRouter(prefix="/etfs", tags=["ETFs Institucionales"])


@router.get(
    "",
    response_model=ETFTrackerResponse,
    summary="Snapshot consolidado del Tracker Institucional de ETFs (BTC & ETH)",
    description="Retorna AUM total, flujos netos diarios, holdings en custodia y desglose por emisor institucional (BlackRock, Fidelity, etc.).",
)
async def get_etf_tracker() -> ETFTrackerResponse:
    """Retorna el estado global de los ETFs Spot de Bitcoin y Ethereum."""
    service = get_etf_service()
    return await service.get_etf_tracker()


@router.get(
    "/btc",
    response_model=ETFSnapshot,
    summary="Métricas de los ETFs Spot de Bitcoin",
    description="Retorna el desglose de los 10 ETFs Spot de Bitcoin aprobados por la SEC.",
)
async def get_btc_etfs() -> ETFSnapshot:
    """Retorna las métricas institucionales de Bitcoin ETFs."""
    service = get_etf_service()
    data = await service.get_etf_tracker()
    return data.btc_etf


@router.get(
    "/eth",
    response_model=ETFSnapshot,
    summary="Métricas de los ETFs Spot de Ethereum",
    description="Retorna el desglose de los ETFs Spot de Ethereum aprobados por la SEC.",
)
async def get_eth_etfs() -> ETFSnapshot:
    """Retorna las métricas institucionales de Ethereum ETFs."""
    service = get_etf_service()
    data = await service.get_etf_tracker()
    return data.eth_etf


@router.get(
    "/history",
    response_model=list[DailyInflowRecord],
    summary="Histórico de flujos netos diarios institucionales",
    description="Retorna los flujos diarios (entradas / salidas netas en USD) para BTC o ETH.",
)
async def get_etf_history(
    asset: str = Query(default="BTC", description="Activo: BTC o ETH"),
) -> list[DailyInflowRecord]:
    """Retorna el histórico de flujos diarios para el activo solicitado."""
    service = get_etf_service()
    data = await service.get_etf_tracker()
    norm = asset.upper().strip()
    if norm == "ETH":
        return data.eth_etf.daily_history
    return data.btc_etf.daily_history
