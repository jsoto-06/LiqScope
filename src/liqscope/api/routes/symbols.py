"""Rutas de la API para consulta de pares y símbolos soportados."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/symbols", tags=["Symbols"])

# Tamaños de bin predeterminados según contrato aprobado
DEFAULT_BIN_SIZES: dict[str, float] = {
    "BTCUSDT": 50.0,
    "ETHUSDT": 10.0,
}


class SymbolConfig(BaseModel):
    """Configuración y parámetros predeterminados de un símbolo perpetuo soportado."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(description="Símbolo del contrato perpetuo (ej. BTCUSDT)")
    default_bin_size: float = Field(gt=0, description="Tamaño de bin predeterminado en USD")


@router.get(
    "",
    response_model=list[SymbolConfig],
    summary="Listado de símbolos admitidos",
    description="Retorna la lista de pares soportados con su tamaño de bin predeterminado.",
)
async def get_symbols() -> list[SymbolConfig]:
    """Devuelve los símbolos actualmente soportados con su default_bin_size."""
    return [
        SymbolConfig(symbol=sym, default_bin_size=DEFAULT_BIN_SIZES[sym])
        for sym in sorted(DEFAULT_BIN_SIZES.keys())
    ]
