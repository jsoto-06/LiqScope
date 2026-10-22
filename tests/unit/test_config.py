"""Tests unitarios para la configuración de LiqScope y validación de valores inválidos."""

import pytest
from pydantic import ValidationError

from liqscope.config import Settings
from liqscope.models.common import Environment, LogLevel


def test_default_settings() -> None:
    """Verifica que la configuración por defecto se instancie correctamente."""
    settings = Settings()
    assert settings.env == Environment.DEMO
    assert settings.port == 8000
    assert settings.log_level == LogLevel.INFO
    assert settings.ws_reconnect_min_delay_sec == 1.0
    assert settings.ws_reconnect_max_delay_sec == 60.0
    assert settings.ws_reconnect_jitter == 0.25
    assert settings.http_request_timeout_sec == 10.0
    assert settings.stale_data_threshold_sec == 30.0


def test_custom_valid_settings() -> None:
    """Verifica la asignación de valores válidos personalizados."""
    settings = Settings(
        env=Environment.PRODUCTION,
        port=9090,
        log_level=LogLevel.DEBUG,
        ws_reconnect_min_delay_sec=2.0,
        ws_reconnect_max_delay_sec=120.0,
        ws_reconnect_jitter=0.5,
        http_request_timeout_sec=15.0,
        stale_data_threshold_sec=45.0,
    )
    assert settings.env == Environment.PRODUCTION
    assert settings.port == 9090
    assert settings.log_level == LogLevel.DEBUG
    assert settings.ws_reconnect_min_delay_sec == 2.0
    assert settings.ws_reconnect_max_delay_sec == 120.0
    assert settings.ws_reconnect_jitter == 0.5


@pytest.mark.parametrize("invalid_port", [0, -1, -8080, 65536, 70000])
def test_invalid_port_raises_validation_error(invalid_port: int) -> None:
    """Verifica que puertos fuera de [1, 65535] lancen ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(port=invalid_port)
    assert "El puerto debe estar entre 1 y 65535" in str(exc_info.value)


@pytest.mark.parametrize("invalid_env", ["staging", "local", "preview", "prod"])
def test_invalid_environment_raises_validation_error(invalid_env: str) -> None:
    """Verifica que entornos no soportados lancen ValidationError."""
    with pytest.raises(ValidationError):
        Settings(env=invalid_env)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid_log_level", ["VERBOSE", "TRACE", "SUPER_DEBUG", ""])
def test_invalid_log_level_raises_validation_error(invalid_log_level: str) -> None:
    """Verifica que niveles de log desconocidos lancen ValidationError."""
    with pytest.raises(ValidationError):
        Settings(log_level=invalid_log_level)  # type: ignore[arg-type]


@pytest.mark.parametrize("invalid_sec", [0.0, -0.5, -10.0])
def test_negative_or_zero_intervals_raise_validation_error(invalid_sec: float) -> None:
    """Verifica que los intervalos temporales menores o iguales a cero sean rechazados."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(ws_reconnect_min_delay_sec=invalid_sec)
    assert "estrictamente positivo" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Settings(http_request_timeout_sec=invalid_sec)
    assert "estrictamente positivo" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        Settings(stale_data_threshold_sec=invalid_sec)
    assert "estrictamente positivo" in str(exc_info.value)


@pytest.mark.parametrize("invalid_jitter", [-0.1, -1.0, 1.01, 2.5])
def test_invalid_jitter_raises_validation_error(invalid_jitter: float) -> None:
    """Verifica que el jitter fuera de [0.0, 1.0] sea rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(ws_reconnect_jitter=invalid_jitter)
    assert "rango [0.0, 1.0]" in str(exc_info.value)


def test_max_delay_smaller_than_min_delay_raises_validation_error() -> None:
    """Verifica que ws_reconnect_max_delay_sec menor que min_delay sea rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        Settings(ws_reconnect_min_delay_sec=10.0, ws_reconnect_max_delay_sec=5.0)
    assert "debe ser mayor o igual que ws_reconnect_min_delay_sec" in str(exc_info.value)


def test_get_settings_singleton_helper() -> None:
    """Verifica que la función helper get_settings retorne una instancia válida."""
    from liqscope.config import get_settings

    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.port == 8000
