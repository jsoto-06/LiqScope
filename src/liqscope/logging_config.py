"""Configuración de logging estructurado en formato JSON para LiqScope."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from liqscope.models.common import LogLevel

SENSITIVE_KEYS: set[str] = {
    "key",
    "secret",
    "password",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "private_key",
}


def mask_sensitive_value(key: str, value: Any) -> Any:
    """Oculta el contenido de variables potencialmente sensibles."""
    if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS):
        return "***REDACTED***"
    if isinstance(value, dict):
        return {k: mask_sensitive_value(str(k), v) for k, v in value.items()}
    if isinstance(value, list):
        return [mask_sensitive_value(key, item) for item in value]
    return value


class StructuredJsonFormatter(logging.Formatter):
    """Formateador de logs que serializa los registros en formato JSON seguro."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }

        # Incluir campos extra que no pertenezcan al record base de logging
        standard_attrs = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
            "asctime",
        }
        for key, value in record.__dict__.items():
            if key not in standard_attrs:
                log_entry[key] = mask_sensitive_value(key, value)

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def setup_logging(log_level: LogLevel = LogLevel.INFO) -> None:
    """Inicializa la configuración de logging raíz de LiqScope."""
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.value)

    # Limpiar handlers previos
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredJsonFormatter())
    root_logger.addHandler(console_handler)
