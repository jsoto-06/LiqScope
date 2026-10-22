"""Implementación de almacenamiento local con SQLite asíncrono (aiosqlite)."""

from datetime import datetime
from pathlib import Path

import aiosqlite

from liqscope.models.common import DataOrigin, Exchange, PositionSide
from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import Trade
from liqscope.storage.base import BaseStorageRepository


class SqliteStorageRepository(BaseStorageRepository):
    """Repositorio SQLite asíncrono para almacenamiento local y pruebas."""

    def __init__(self, database_path: str | Path = "./data/liqscope.db") -> None:
        self.database_path = Path(database_path)
        self._db: aiosqlite.Connection | None = None

    async def initialize(self) -> None:
        """Inicializa el archivo de base de datos y crea las tablas e índices si no existen."""
        # Asegurar que el directorio contenedor exista si no es en memoria
        if str(self.database_path) != ":memory:":
            self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = await aiosqlite.connect(str(self.database_path))
        self._db.row_factory = aiosqlite.Row

        # Habilitar modo WAL para concurrencia óptima de lecturas y escrituras
        await self._db.execute("PRAGMA journal_mode = WAL;")
        await self._db.execute("PRAGMA synchronous = NORMAL;")

        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                side TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                trade_id TEXT
            );
        """)
        await self._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_trades_symbol_ts
            ON trades (symbol, timestamp DESC);
        """)

        await self._db.execute("""
            CREATE TABLE IF NOT EXISTS liquidations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exchange TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                quantity REAL NOT NULL,
                filled_quantity REAL NOT NULL,
                usd_volume REAL NOT NULL,
                timestamp TEXT NOT NULL,
                origin TEXT NOT NULL
            );
        """)
        await self._db.execute("""
            CREATE INDEX IF NOT EXISTS idx_liquidations_symbol_ts
            ON liquidations (symbol, timestamp DESC);
        """)
        await self._db.commit()

    async def close(self) -> None:
        """Cierra la conexión con SQLite."""
        if self._db:
            await self._db.close()
            self._db = None

    async def record_trade(self, trade: Trade) -> None:
        """Inserta una operación de mercado en la base de datos."""
        if self._db is None:
            raise RuntimeError("Base de datos no inicializada. Llame a initialize() primero.")

        await self._db.execute(
            """
            INSERT INTO trades (exchange, symbol, price, quantity, side, timestamp, trade_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trade.exchange.value,
                trade.symbol,
                trade.price,
                trade.quantity,
                trade.side.value,
                trade.timestamp.isoformat(),
                str(trade.trade_id) if trade.trade_id is not None else None,
            ),
        )
        await self._db.commit()

    async def record_liquidation(self, liquidation: LiquidationEvent) -> None:
        """Inserta un evento de liquidación forzada en la base de datos."""
        if self._db is None:
            raise RuntimeError("Base de datos no inicializada. Llame a initialize() primero.")

        await self._db.execute(
            """
            INSERT INTO liquidations (
                exchange, symbol, side, price, quantity, filled_quantity, usd_volume, timestamp, origin
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                liquidation.exchange.value,
                liquidation.symbol,
                liquidation.side.value,
                liquidation.price,
                liquidation.quantity,
                liquidation.filled_quantity,
                liquidation.usd_volume,
                liquidation.timestamp.isoformat(),
                liquidation.origin.value,
            ),
        )
        await self._db.commit()

    async def get_recent_liquidations(
        self,
        symbol: str,
        limit: int = 100,
    ) -> list[LiquidationEvent]:
        """Obtiene las liquidaciones más recientes para un símbolo."""
        if self._db is None:
            raise RuntimeError("Base de datos no inicializada. Llame a initialize() primero.")

        cursor = await self._db.execute(
            """
            SELECT exchange, symbol, side, price, quantity, filled_quantity, usd_volume, timestamp, origin
            FROM liquidations
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (symbol.upper(), limit),
        )
        rows = await cursor.fetchall()
        return [
            LiquidationEvent(
                exchange=Exchange(row["exchange"]),
                symbol=row["symbol"],
                side=PositionSide(row["side"]),
                price=float(row["price"]),
                quantity=float(row["quantity"]),
                filled_quantity=float(row["filled_quantity"]),
                usd_volume=float(row["usd_volume"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                origin=DataOrigin(row["origin"]),
            )
            for row in rows
        ]

    async def get_recent_trades(
        self,
        symbol: str,
        limit: int = 100,
    ) -> list[Trade]:
        """Obtiene las operaciones más recientes para un símbolo."""
        if self._db is None:
            raise RuntimeError("Base de datos no inicializada. Llame a initialize() primero.")

        cursor = await self._db.execute(
            """
            SELECT exchange, symbol, price, quantity, side, timestamp, trade_id
            FROM trades
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (symbol.upper(), limit),
        )
        rows = await cursor.fetchall()
        return [
            Trade(
                exchange=Exchange(row["exchange"]),
                symbol=row["symbol"],
                price=float(row["price"]),
                quantity=float(row["quantity"]),
                side=PositionSide(row["side"]),
                timestamp=datetime.fromisoformat(row["timestamp"]),
                trade_id=row["trade_id"],
            )
            for row in rows
        ]
