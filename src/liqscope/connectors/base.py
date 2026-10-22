"""Interfaz abstracta y estados para conectores de fuentes de datos (DataSource)."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from enum import StrEnum
from typing import Any

from liqscope.models.common import Exchange
from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import Trade

TradeHandler = Callable[[Trade], Coroutine[Any, Any, None]]
LiquidationHandler = Callable[[LiquidationEvent], Coroutine[Any, Any, None]]


class ConnectionStatus(StrEnum):
    """Estados del ciclo de vida de conexión de un conector."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"


class DataSource(ABC):
    """Clase base abstracta para cualquier conector de datos de exchange."""

    def __init__(self, exchange: Exchange) -> None:
        self.exchange = exchange
        self._status: ConnectionStatus = ConnectionStatus.DISCONNECTED
        self._trade_handlers: list[TradeHandler] = []
        self._liquidation_handlers: list[LiquidationHandler] = []

    @property
    def status(self) -> ConnectionStatus:
        """Retorna el estado actual de la conexión."""
        return self._status

    @property
    def is_connected(self) -> bool:
        """Indica si el conector está activo y conectado."""
        return self._status == ConnectionStatus.CONNECTED

    def register_trade_handler(self, handler: TradeHandler) -> None:
        """Registra una función callback asíncrona para eventos de trade."""
        self._trade_handlers.append(handler)

    def register_liquidation_handler(self, handler: LiquidationHandler) -> None:
        """Registra una función callback asíncrona para eventos de liquidación."""
        self._liquidation_handlers.append(handler)

    async def emit_trade(self, trade: Trade) -> None:
        """Notifica a todos los manejadores registrados la recepción de un trade."""
        for handler in self._trade_handlers:
            await handler(trade)

    async def emit_liquidation(self, liquidation: LiquidationEvent) -> None:
        """Notifica a todos los manejadores registrados la recepción de una liquidación."""
        for handler in self._liquidation_handlers:
            await handler(liquidation)

    @abstractmethod
    async def start(self) -> None:
        """Inicia el bucle de ingesta y conexión."""
        raise NotImplementedError

    @abstractmethod
    async def stop(self) -> None:
        """Detiene de forma limpia (graceful shutdown) la conexión y tareas en curso."""
        raise NotImplementedError
