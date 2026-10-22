"""Modelos de mercado: operaciones ejecutadas y open interest."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from liqscope.models.common import Exchange, PositionSide


class Trade(BaseModel):
    """Modelo normalizado para una operación ejecutada (trade/aggTrade)."""

    model_config = ConfigDict(frozen=True)

    exchange: Exchange = Field(description="Exchange de origen de la operación")
    symbol: str = Field(description="Símbolo del par (ej. BTCUSDT)")
    price: float = Field(gt=0, description="Precio de ejecución de la operación")
    quantity: float = Field(gt=0, description="Volumen/cantidad operada en contratos/base")
    side: PositionSide = Field(description="Lado agresor/tomador (LONG/BUY o SHORT/SELL)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Marca de tiempo en UTC",
    )
    trade_id: str | int | None = Field(
        default=None,
        description="Identificador único del trade asignado por el exchange",
    )


class OpenInterestSnapshot(BaseModel):
    """Instantánea de interés abierto (Open Interest) para un símbolo."""

    model_config = ConfigDict(frozen=True)

    exchange: Exchange = Field(description="Exchange de origen")
    symbol: str = Field(description="Símbolo del par (ej. BTCUSDT)")
    open_interest: float = Field(ge=0, description="Interés abierto en contratos o unidades base")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Marca de tiempo en UTC",
    )
