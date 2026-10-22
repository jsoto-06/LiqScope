"""Interfaz abstracta para la capa de almacenamiento y persistencia."""

from abc import ABC, abstractmethod

from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import Trade


class BaseStorageRepository(ABC):
    """Interfaz abstracta que define las operaciones de persistencia de LiqScope.

    Permite desacoplar el motor y los conectores de la base de datos específica,
    facilitando la migración desde SQLite (desarrollo) a PostgreSQL/TimescaleDB (producción).
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Crea tablas e índices necesarios si no existen."""
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        """Cierra el pool de conexiones de la base de datos de forma limpia."""
        raise NotImplementedError

    @abstractmethod
    async def record_trade(self, trade: Trade) -> None:
        """Persiste una operación de mercado."""
        raise NotImplementedError

    @abstractmethod
    async def record_liquidation(self, liquidation: LiquidationEvent) -> None:
        """Persiste un evento de liquidación forzada."""
        raise NotImplementedError

    @abstractmethod
    async def get_recent_liquidations(
        self,
        symbol: str,
        limit: int = 100,
    ) -> list[LiquidationEvent]:
        """Recupera los eventos de liquidación más recientes para un símbolo."""
        raise NotImplementedError

    @abstractmethod
    async def get_recent_trades(
        self,
        symbol: str,
        limit: int = 100,
    ) -> list[Trade]:
        """Recupera las operaciones más recientes para un símbolo."""
        raise NotImplementedError
