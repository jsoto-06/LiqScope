"""Rutas de API para el Screener de Mercado: Ganadoras, Perdedoras y Detección de Ballenas."""

from __future__ import annotations

from fastapi import APIRouter

from liqscope.models.screener import ScreenerItem, ScreenerResponse
from liqscope.services.screener_service import get_screener_service

router = APIRouter(prefix="/screener", tags=["Screener & Ballenas"])


@router.get(
    "",
    response_model=ScreenerResponse,
    summary="Snapshot consolidado del Screener de Mercado y Radar de Ballenas",
    description="Retorna amplitud de mercado, top ganadoras, top perdedoras, picos inusuales de Open Interest y lista completa.",
)
async def get_screener() -> ScreenerResponse:
    """Retorna el estado integral del screener de derivados."""
    service = get_screener_service()
    return await service.get_screener_data()


@router.get(
    "/gainers",
    response_model=list[ScreenerItem],
    summary="Top Ganadoras (24h) en derivados",
    description="Retorna el ranking de las 15 monedas con mayor subida porcentual en 24h.",
)
async def get_top_gainers() -> list[ScreenerItem]:
    """Retorna las principales ganadoras del mercado."""
    service = get_screener_service()
    data = await service.get_screener_data()
    return data.top_gainers


@router.get(
    "/losers",
    response_model=list[ScreenerItem],
    summary="Top Perdedoras (24h) en derivados",
    description="Retorna el ranking de las 15 monedas con mayor caída porcentual en 24h.",
)
async def get_top_losers() -> list[ScreenerItem]:
    """Retorna las principales perdedoras del mercado."""
    service = get_screener_service()
    data = await service.get_screener_data()
    return data.top_losers


@router.get(
    "/oi-surge",
    response_model=list[ScreenerItem],
    summary="Radar de Ballenas (OI Surge & Acumulación Institucional)",
    description="Retorna activos con picos agresivos de Open Interest y anomalías de volumen institucional.",
)
async def get_oi_surge() -> list[ScreenerItem]:
    """Retorna el radar de picos de Open Interest y ballenas."""
    service = get_screener_service()
    data = await service.get_screener_data()
    return data.oi_surge
