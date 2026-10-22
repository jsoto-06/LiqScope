"""Modelos comunes y enumeraciones para LiqScope."""

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
    """Origen del dato: real (on-chain Hyperliquid) o estimado (CEX)."""

    REAL = "real"
    ESTIMATED = "estimated"


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
