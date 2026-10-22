"""Tests unitarios para la configuración de logging estructurado en JSON."""

import json
import logging

from liqscope.logging_config import StructuredJsonFormatter, mask_sensitive_value, setup_logging
from liqscope.models.common import LogLevel


def test_mask_sensitive_value() -> None:
    """Verifica que las claves sensibles sean enmascaradas."""
    assert mask_sensitive_value("api_key", "secret123") == "***REDACTED***"
    assert mask_sensitive_value("authorization", "Bearer xyz") == "***REDACTED***"
    assert mask_sensitive_value("api_secret", "my_secret") == "***REDACTED***"
    assert mask_sensitive_value("public_symbol", "BTCUSDT") == "BTCUSDT"

    nested = {"api_key": "12345", "user": "trader"}
    masked = mask_sensitive_value("config", nested)
    assert masked == {"api_key": "***REDACTED***", "user": "trader"}

    nested_list = [{"api_key": "abc"}, {"public": "xyz"}]
    masked_list = mask_sensitive_value("items", nested_list)
    assert masked_list == [{"api_key": "***REDACTED***"}, {"public": "xyz"}]


def test_structured_json_formatter_with_exception() -> None:
    """Verifica que las excepciones sean formateadas dentro del objeto JSON."""
    formatter = StructuredJsonFormatter()
    try:
        raise RuntimeError("Fallo simulado para test")
    except RuntimeError:
        import sys

        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="liqscope.error",
        level=logging.ERROR,
        pathname=__file__,
        lineno=50,
        msg="Error con traza",
        args=(),
        exc_info=exc_info,
    )
    formatted_str = formatter.format(record)
    data = json.loads(formatted_str)
    assert data["level"] == "ERROR"
    assert "exception" in data
    assert "Fallo simulado para test" in data["exception"]


def test_structured_json_formatter() -> None:
    """Verifica que el formateador produzca JSON válido con los campos requeridos."""
    formatter = StructuredJsonFormatter()
    record = logging.LogRecord(
        name="liqscope.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    # Agregar atributo sensible adicional en el diccionario del registro
    record.__dict__["api_secret"] = "sensitive_token_value"

    formatted_str = formatter.format(record)
    data = json.loads(formatted_str)

    assert data["level"] == "INFO"
    assert data["logger"] == "liqscope.test"
    assert data["message"] == "Test message"
    assert "timestamp" in data
    assert data.get("api_secret") == "***REDACTED***"


def test_setup_logging_initialization() -> None:
    """Verifica que setup_logging configure el root logger correctamente."""
    setup_logging(LogLevel.DEBUG)
    root = logging.getLogger()
    assert root.level == logging.DEBUG
    assert len(root.handlers) >= 1
    assert any(isinstance(h.formatter, StructuredJsonFormatter) for h in root.handlers)
