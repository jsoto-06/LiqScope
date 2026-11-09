"""Modelos de datos para el mapa de calor (Heatmap) de liquidaciones estimadas."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field

from liqscope.models.common import DataCoverage, DataOrigin, PositionSide

DEFAULT_DISCLAIMER: str = (
    "Niveles de liquidación estimados modelados a partir de Open Interest agregado bajo el "
    "supuesto de assumed_long_ratio = 0.50 y parámetros arbitrarios de MMR (MMR < 1/L). El tramo "
    "5x es ilustrativo. Se ignoran comisiones de trading, comisiones de liquidación, tasas de "
    "financiación y mecánicas de colateral de margen cruzado. No refleja posiciones individuales "
    "reales, precios de entrada reales ni sesgo direccional del mercado."
)


class LiquidationLevel(BaseModel):
    """Nivel discreto de liquidación estimado para un apalancamiento y tamaño dados."""

    model_config = ConfigDict(frozen=True)

    price: float = Field(gt=0, description="Precio estimado de liquidación")
    volume_usd: float = Field(gt=0, description="Volumen estimado en USD en este nivel")
    leverage: float = Field(gt=0, description="Apalancamiento asociado (ej. 10x, 25x)")
    side: PositionSide = Field(description="Dirección de la posición liquidada (LONG o SHORT)")
    origin: DataOrigin = Field(
        default=DataOrigin.MODELED,
        description="Origen del dato (OBSERVED o MODELED)",
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
        default=DataOrigin.MODELED,
        description="Origen del dato (OBSERVED o MODELED)",
    )
    coverage: DataCoverage = Field(
        default=DataCoverage.NA,
        description="Cobertura del flujo de datos según ADR-011 (por defecto NA para MODELED)",
    )
    dominant_leverage: float | None = Field(
        default=None,
        description="Apalancamiento dominante responsable de la mayor liquidez en este bin (ej. 25x, 50x, 100x)",
    )
    leverages: list[float] = Field(
        default_factory=list,
        description="Lista de apalancamientos que contribuyen a este bin",
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
    total_open_interest_usd: float = Field(
        default=0.0,
        ge=0,
        description="Interés abierto total en USD",
    )
    visible_bin_volume_usd: float = Field(
        default=0.0,
        ge=0,
        description="Volumen total acumulado en USD en los bins visibles",
    )
    coverage_pct: float = Field(
        default=0.0,
        ge=0,
        le=100,
        description="Porcentaje de cobertura de volumen de bins visibles vs total OI",
    )
    assumed_long_ratio: float = Field(
        default=0.50,
        ge=0,
        le=1,
        description="Ratio supuesto de posiciones long (0.50 neutro)",
    )
    source: str = Field(
        default="live",
        description="Origen de los datos: 'live' o 'demo'",
    )
    disclaimer: str = Field(
        default=DEFAULT_DISCLAIMER,
        description="Aviso analítico y advertencia de supuestos del modelo",
    )
    cached: bool = Field(
        default=False,
        description="Indica si los datos de mercado fueron obtenidos de la caché local",
    )
    data_age_sec: float = Field(
        default=0.0,
        ge=0,
        description="Antigüedad en segundos de los datos de mercado utilizados",
    )
    long_account_ratio: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Ratio real de cuentas en largo según telemetría de Binance",
    )
    short_account_ratio: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Ratio real de cuentas en corto según telemetría de Binance",
    )
    ratio_source: str = Field(
        default="live",
        description="Fuente del ratio: 'live' (Binance Long/Short accounts), 'custom' o 'neutral'",
    )
    total_estimated_volume_usd: float = Field(
        default=0.0,
        ge=0,
        description="Suma total de volumen nocional en USD contenido en el snapshot (compatibilidad)",
    )
    is_complete: bool = Field(
        default=True,
        description="Indica si el snapshot contiene datos íntegros o presenta huecos temporales",
    )
    exchange: str = Field(
        default="all",
        description="Exchange de origen o 'all' para agregación global multi-exchange",
    )
    exchange_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Desglose del Open Interest nocional en USD por exchange (Binance, Bybit, Hyperliquid, Kraken)",
    )
    timeframe: str = Field(
        default="24h",
        description="Horizonte temporal de acumulación de posiciones LiqScope ('12h', '24h', '3d', '1w', '1m', '3m')",
    )
