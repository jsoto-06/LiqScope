"""Modelos de datos para el feed de liquidaciones forzadas reales en tiempo real."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LiquidationEvent(BaseModel):
    """Evento de liquidación forzada real ejecutada en el mercado de derivados."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(description="Símbolo del par derivado (ej. BTCUSDT)")
    side: str = Field(description="Dirección de la orden de liquidación (SELL o BUY)")
    liquidated_side: str = Field(description="Posición del operador liquidado: LONG o SHORT")
    price: float = Field(gt=0, description="Precio de liquidación base del contrato")
    avg_price: float = Field(gt=0, description="Precio medio de ejecución real en el libro")
    quantity: float = Field(gt=0, description="Cantidad liquidada en contratos/monedas")
    volume_usd: float = Field(ge=0, description="Volumen total nocional liquidado en USD")
    timestamp: int = Field(description="Marca temporal Unix en milisegundos")
    is_whale: bool = Field(default=False, description="True si el volumen supera $100,000 USD")
    is_mega_whale: bool = Field(default=False, description="True si el volumen supera $500,000 USD")
    exchange: str = Field(default="binance", description="Exchange de origen de la liquidación")


class LiquidationStats(BaseModel):
    """Métricas acumuladas de liquidaciones observadas durante la sesión."""

    model_config = ConfigDict(frozen=True)

    total_count: int = Field(default=0, ge=0)
    total_volume_usd: float = Field(default=0.0, ge=0)
    long_count: int = Field(default=0, ge=0)
    long_volume_usd: float = Field(default=0.0, ge=0)
    short_count: int = Field(default=0, ge=0)
    short_volume_usd: float = Field(default=0.0, ge=0)
    whale_count: int = Field(default=0, ge=0)
    largest_event: LiquidationEvent | None = Field(default=None)
