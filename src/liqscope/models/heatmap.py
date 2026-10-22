"""Modelos de datos para el mapa de calor (Heatmap) de liquidaciones estimadas."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from liqscope.models.common import DataOrigin, PositionSide


class LiquidationLevel(BaseModel):
    """Nivel discreto de liquidación estimado para un apalancamiento y tamaño dados."""

    model_config = ConfigDict(frozen=True)

    price: float = Field(gt=0, description="Precio estimado de liquidación")
    volume_usd: float = Field(gt=0, description="Volumen estimado en USD en este nivel")
    leverage: float = Field(gt=0, description="Apalancamiento asociado (ej. 10x, 25x)")
    side: PositionSide = Field(description="Dirección de la posición liquidada (LONG o SHORT)")
    origin: DataOrigin = Field(
        default=DataOrigin.ESTIMATED,
        description="Origen del dato (REAL o ESTIMATED)",
    )


class HeatmapBin(BaseModel):
    """Bin o celda agregada de precio en el mapa de calor."""

    model_config = ConfigDict(frozen=True)

    price_min: float = Field(gt=0, description="Límite inferior del rango de precio del bin")
    price_max: float = Field(gt=0, description="Límite superior del rango de precio del bin")
    price_mid: float = Field(gt=0, description="Punto medio del bin para referencia visual")
    estimated_volume_usd: float = Field(
        ge=0,
        description="Volumen total acumulado en USD en este rango de precio",
    )
    long_volume_usd: float = Field(
        default=0.0,
        ge=0,
        description="Volumen estimado de posiciones LONG liquidables",
    )
    short_volume_usd: float = Field(
        default=0.0,
        ge=0,
        description="Volumen estimado de posiciones SHORT liquidables",
    )
    estimated_positions: int = Field(
        default=0,
        ge=0,
        description="Número estimado de posiciones concentradas en este bin",
    )
    origin: DataOrigin = Field(
        default=DataOrigin.ESTIMATED,
        description="Origen del dato (REAL o ESTIMATED)",
    )


class HeatmapSnapshot(BaseModel):
    """Instantánea completa del mapa de calor de liquidaciones para un par."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(description="Símbolo del par (ej. BTCUSDT)")
    current_price: float = Field(gt=0, description="Precio de referencia de mercado actual")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Marca de tiempo de generación del snapshot",
    )
    bin_size: float = Field(gt=0, description="Tamaño del intervalo de cada bin en USD")
    bins: list[HeatmapBin] = Field(description="Lista de bins agregados ordenados por precio")
    total_estimated_volume_usd: float = Field(
        ge=0,
        description="Suma total de volumen nocional en USD contenido en el snapshot",
    )
    is_complete: bool = Field(
        default=True,
        description="Indica si el snapshot contiene datos íntegros o presenta huecos temporales",
    )
