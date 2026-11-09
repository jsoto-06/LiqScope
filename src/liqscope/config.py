"""Configuración central de la aplicación mediante Pydantic Settings."""

from pathlib import Path
from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from liqscope.models.common import Environment, LogLevel


class Settings(BaseSettings):
    """Configuración global de LiqScope validada estrictamente."""

    model_config = SettingsConfigDict(
        env_prefix="LIQSCOPE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Entorno y servidor
    env: Environment = Field(
        default=Environment.DEMO,
        description="Entorno de ejecución: demo, development, production, test",
    )
    host: str = Field(default="127.0.0.1", description="Host de enlace para el servidor API")
    port: int = Field(default=8000, description="Puerto TCP del servidor (1-65535)")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"],
        description="Orígenes CORS permitidos",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Permitir cookies y credenciales en peticiones CORS",
    )

    # Logging
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Nivel mínimo de log")

    # Persistencia
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/liqscope.db",
        description="URL de conexión a la base de datos (SQLAlchemy / aiosqlite)",
    )
    data_dir: Path = Field(
        default=Path("./data"),
        description="Directorio para almacenamiento de datos locales y snapshots",
    )

    # Endpoints oficiales de exchanges (Solo lectura)
    binance_ws_url: str = Field(
        default="wss://fstream.binance.com/ws",
        description="URL oficial de WebSocket Binance Futures USDⓈ-M",
    )
    binance_rest_url: str = Field(
        default="https://fapi.binance.com",
        description="URL oficial de API REST Binance Futures USDⓈ-M",
    )
    bybit_ws_url: str = Field(
        default="wss://stream.bybit.com/v5/public/linear",
        description="URL oficial de WebSocket Bybit Linear",
    )
    bybit_rest_url: str = Field(
        default="https://api.bybit.com",
        description="URL oficial de API REST Bybit",
    )
    hyperliquid_info_url: str = Field(
        default="https://api.hyperliquid.xyz/info",
        description="URL oficial de la API Info de Hyperliquid",
    )
    kraken_futures_rest_url: str = Field(
        default="https://futures.kraken.com/derivatives/api/v3",
        description="URL oficial de la API REST de Kraken Futures",
    )

    # Robustez, timeouts y reconexión
    ws_reconnect_min_delay_sec: float = Field(
        default=1.0,
        description="Demora mínima inicial para reconexión con backoff exponencial",
    )
    ws_reconnect_max_delay_sec: float = Field(
        default=60.0,
        description="Demora máxima permitida para reconexión con backoff exponencial",
    )
    ws_reconnect_jitter: float = Field(
        default=0.25,
        description="Factor de jitter aleatorio [0.0, 1.0] para evitar tormentas de reconexión",
    )
    http_request_timeout_sec: float = Field(
        default=5.0,
        description="Timeout máximo en segundos para llamadas REST",
    )
    market_data_cache_ttl_sec: float = Field(
        default=10.0,
        description="Tiempo de vida (TTL) en segundos para la caché en memoria de Binance",
    )
    stale_data_threshold_sec: float = Field(
        default=30.0,
        description="Tiempo en segundos a partir del cual un snapshot se marca como obsoleto",
    )

    # Configuración de distribución de apalancamiento
    distribution_config_path: Path = Field(
        default=Path("./config/default_distribution.yaml"),
        description="Ruta al archivo YAML de pesos y supuestos de apalancamiento",
    )

    # Notificaciones y alertas externas (Telegram Bot)
    telegram_bot_token: str = Field(
        default="",
        description="Token de autorización del Bot de Telegram (ej. 123456:ABC-DEF)",
    )
    telegram_chat_id: str = Field(
        default="",
        description="ID numérico o @canal del chat receptor de alertas en Telegram",
    )
    telegram_alerts_enabled: bool = Field(
        default=False,
        description="Indica si el envío automático de alertas a Telegram está habilitado",
    )
    telegram_min_volume_usd: float = Field(
        default=50_000_000.0,
        ge=0,
        description="Volumen nocional mínimo en USD para considerar una alerta en Telegram",
    )
    telegram_max_delta_pct: float = Field(
        default=1.5,
        gt=0,
        description="Distancia porcentual máxima al Mark Price para activar alerta en Telegram",
    )

    @field_validator("binance_ws_url", "bybit_ws_url")
    @classmethod
    def validate_ws_url(cls, v: str) -> str:
        """Valida que la URL del WebSocket utilice un esquema ws:// o wss:// válido."""
        if not (v.startswith("wss://") or v.startswith("ws://")):
            raise ValueError(f"La URL de WebSocket debe iniciar con ws:// o wss://, recibido: {v}")
        return v

    @field_validator("port")
    @classmethod
    def validate_port_range(cls, v: int) -> int:
        """Valida que el puerto se encuentre en el rango TCP válido [1, 65535]."""
        if not (1 <= v <= 65535):
            raise ValueError(f"El puerto debe estar entre 1 y 65535, recibido: {v}")
        return v

    @field_validator(
        "ws_reconnect_min_delay_sec",
        "ws_reconnect_max_delay_sec",
        "http_request_timeout_sec",
        "market_data_cache_ttl_sec",
        "stale_data_threshold_sec",
    )
    @classmethod
    def validate_positive_seconds(cls, v: float) -> float:
        """Valida que los tiempos y demoras sean números estrictamente positivos."""
        if v <= 0:
            raise ValueError(
                f"El intervalo de tiempo debe ser estrictamente positivo (>0), recibido: {v}"
            )
        return v

    @field_validator("ws_reconnect_jitter")
    @classmethod
    def validate_jitter_range(cls, v: float) -> float:
        """Valida que el jitter esté acotado entre 0.0 y 1.0."""
        if not (0.0 <= v <= 1.0):
            raise ValueError(f"El jitter debe estar en el rango [0.0, 1.0], recibido: {v}")
        return v

    @model_validator(mode="after")
    def validate_reconnect_delays(self) -> Self:
        """Verifica que max_delay sea mayor o igual que min_delay."""
        if self.ws_reconnect_max_delay_sec < self.ws_reconnect_min_delay_sec:
            raise ValueError(
                f"ws_reconnect_max_delay_sec ({self.ws_reconnect_max_delay_sec}) debe ser mayor o igual "
                f"que ws_reconnect_min_delay_sec ({self.ws_reconnect_min_delay_sec})"
            )
        return self

    @model_validator(mode="after")
    def validate_cors_security(self) -> Self:
        """Rechaza comodín '*' en cors_origins cuando cors_allow_credentials está activo."""
        if self.cors_allow_credentials and "*" in self.cors_origins:
            raise ValueError(
                "Configuración CORS insegura: No se permite '*' en 'cors_origins' "
                "cuando 'cors_allow_credentials' está habilitado (riesgo de fuga de credenciales)."
            )
        return self


# Instancia singleton predeterminada
def get_settings() -> Settings:
    """Retorna una instancia de configuración."""
    return Settings()
