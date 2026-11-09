"""Rutas de API para el módulo de Tasas de Financiación (Funding Rates)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from liqscope.models.funding import FundingItem, FundingMatrixResponse
from liqscope.services.funding_service import get_funding_service

router = APIRouter(prefix="/funding", tags=["Funding Rates"])


@router.get(
    "",
    response_model=FundingMatrixResponse,
    summary="Matriz completa de tasas de financiación multi-exchange",
    description="Retorna la matriz consolidada de tasas de financiación de Binance y Bybit para las principales criptomonedas.",
)
async def get_funding_matrix() -> FundingMatrixResponse:
    """Retorna la matriz global de funding rates."""
    service = get_funding_service()
    return await service.get_funding_matrix()


@router.get(
    "/{symbol}",
    response_model=FundingItem,
    summary="Tasa de financiación para un par específico",
    description="Retorna la tasa actual, anualizada y el tiempo restante de liquidación para el par indicado.",
)
async def get_symbol_funding(symbol: str) -> FundingItem:
    """Retorna la tasa de funding para un par específico."""
    service = get_funding_service()
    item = await service.get_symbol_funding(symbol)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontraron datos de financiación para el símbolo '{symbol}'.",
        )
    return item
