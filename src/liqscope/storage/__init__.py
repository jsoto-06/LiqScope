"""Módulo de persistencia y almacenamiento de LiqScope."""

from liqscope.storage.base import BaseStorageRepository
from liqscope.storage.sqlite import SqliteStorageRepository

__all__ = [
    "BaseStorageRepository",
    "SqliteStorageRepository",
]
