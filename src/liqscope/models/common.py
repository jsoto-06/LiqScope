"""Modelos comunes y enumeraciones para LiqScope."""

from __future__ import annotations

from enum import StrEnum


class Exchange(StrEnum):
    """Exchanges soportados por LiqScope."""

    BINANCE = "binance"
    BYBIT = "bybit"
    HYPERLIQUID = "hyperliquid"
    DEMO = "demo"


class PositionSide(StrEnum):
    """Dirección de la posición."""

    LONG = "long"
    SHORT = "short"
    BOTH = "both"


class TradeSide(StrEnum):
    """Lado agresor/tomador de una operación de mercado ejecutada."""

    AGGRESSIVE_BUY = "AGGRESSIVE_BUY"
    AGGRESSIVE_SELL = "AGGRESSIVE_SELL"


class DataOrigin(StrEnum):
    """Origen del dato según ADR-011: observado directamente o modelado analíticamente."""

    OBSERVED = "observed"
    MODELED = "modeled"
    REAL = "real"
    ESTIMATED = "estimated"

    @classmethod
    def _missing_(cls, value: object) -> DataOrigin | None:
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class DataCoverage(StrEnum):
    """Cobertura del flujo de datos según ADR-011."""

    COMPLETE = "complete"
    SAMPLED = "sampled"
    NA = "na"

    @classmethod
    def _missing_(cls, value: object) -> DataCoverage | None:
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None


class DataSourceType(StrEnum):
    """Mecanismo de ingesta de datos."""

    WEBSOCKET = "websocket"
    REST = "rest"
    DEMO_FIXTURE = "demo_fixture"


class Environment(StrEnum):
    """Entorno de ejecución de la aplicación."""

    DEMO = "demo"
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(StrEnum):
    """Niveles de registro de logging estándar."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
