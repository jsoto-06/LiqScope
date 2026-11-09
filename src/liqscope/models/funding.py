"""Modelos de datos para el módulo de Tasas de Financiación (Funding Rates)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class FundingItem(BaseModel):
    """Información de tasa de financiación para un par específico."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(description="Símbolo del par (ej. BTCUSDT)")
    mark_price: float = Field(default=0.0, ge=0.0, description="Precio Mark actual de referencia")
    index_price: float = Field(default=0.0, ge=0.0, description="Precio de índice subyacente")
    binance_rate: float = Field(default=0.0, description="Tasa de financiación de Binance (en % por 8h)")
    bybit_rate: float = Field(default=0.0, description="Tasa de financiación de Bybit (en % por 8h)")
    average_rate: float = Field(default=0.0, description="Media de financiación entre exchanges (%)")
    annualized_apr: float = Field(default=0.0, description="Tasa anualizada nominal APR (%)")
    next_funding_time_ms: int = Field(default=0, description="Timestamp Unix en ms de la próxima liquidación")
    seconds_until_funding: int = Field(default=0, ge=0, description="Segundos restantes para el cobro/pago")
    bias: Literal["LONGS_PAY", "SHORTS_PAY", "NEUTRAL"] = Field(
        default="NEUTRAL",
        description="Dirección del flujo de comisiones",
    )
    thermal_state: Literal[
        "OVERHEATED_LONG", "WARM_LONG", "NEUTRAL", "WARM_SHORT", "OVERHEATED_SHORT"
    ] = Field(
        default="NEUTRAL",
        description="Nivel térmico de sobrecalentamiento del mercado",
    )


class FundingMatrixResponse(BaseModel):
    """Respuesta consolidada con la matriz completa de tasas de financiación multi-exchange."""

    model_config = ConfigDict(frozen=True)

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Timestamp de la consulta",
    )
    items: list[FundingItem] = Field(
        default_factory=list,
        description="Lista de pares con tasas y métricas de financiación",
    )
    next_funding_time_ms: int = Field(default=0, description="Timestamp de la próxima liquidación global")
    seconds_until_funding: int = Field(default=0, ge=0, description="Segundos hasta la próxima liquidación")
    market_bias: str = Field(default="NEUTRAL", description="Sesgo ponderado global del mercado")
    average_market_rate: float = Field(default=0.0, description="Media global de tasas de las principales criptomonedas")
    overheated_longs_count: int = Field(default=0, description="Número de pares sobrecalentados en compra (euforia)")
    overheated_shorts_count: int = Field(default=0, description="Número de pares sobrecalentados en venta (pesimismo)")
