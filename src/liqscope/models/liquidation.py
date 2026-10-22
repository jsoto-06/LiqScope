"""Modelos de eventos de liquidación forzada de posiciones."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from liqscope.models.common import DataCoverage, DataOrigin, Exchange, PositionSide


class LiquidationEvent(BaseModel):
    """Evento normalizado de liquidación forzada emitido por un exchange."""

    model_config = ConfigDict(frozen=True)

    exchange: Exchange = Field(description="Exchange de origen de la liquidación")
    symbol: str = Field(description="Símbolo del par (ej. BTCUSDT)")
    side: PositionSide = Field(
        description="Lado de la posición que fue liquidada (LONG o SHORT)",
    )
    price: float | None = Field(
        default=None,
        gt=0,
        description="Precio de ejecución de la orden forzada (si está disponible)",
    )
    bankruptcy_price: float | None = Field(
        default=None,
        gt=0,
        description="Precio de bancarrota reportado por el exchange",
    )
    quantity: float = Field(gt=0, description="Cantidad total de la orden de liquidación")
    filled_quantity: float = Field(
        ge=0,
        description="Cantidad ejecutada/llenada de la liquidación",
    )
    usd_volume: float = Field(
        gt=0,
        description="Volumen nocional aproximado en USD (precio * cantidad)",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Marca de tiempo en UTC del evento",
    )
    origin: DataOrigin = Field(
        default=DataOrigin.OBSERVED,
        description="Naturaleza del dato según ADR-011: OBSERVED o MODELED",
    )
    coverage: DataCoverage = Field(
        default=DataCoverage.COMPLETE,
        description="Cobertura del stream según ADR-011: COMPLETE o SAMPLED",
    )
    incomplete: bool = Field(
        default=False,
        description="Indica si hubo pérdida de continuidad por desconexión en el stream",
    )
