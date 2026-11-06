"""Tests unitarios para el repositorio SQLite de almacenamiento."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from liqscope.models.common import DataOrigin, Exchange, PositionSide, TradeSide
from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import Trade
from liqscope.storage.sqlite import SqliteStorageRepository


@pytest.mark.asyncio
async def test_sqlite_storage_lifecycle_and_crud() -> None:
    """Verifica el ciclo completo de inicialización, inserción y recuperación en SQLite."""
    storage = SqliteStorageRepository(database_path=":memory:")
    await storage.initialize()

    now = datetime.now(UTC)

    # 1. Probar Trade CRUD
    trade = Trade(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        price=68200.0,
        quantity=0.5,
        side=TradeSide.AGGRESSIVE_BUY,
        timestamp=now,
        trade_id="trade_1001",
    )
    await storage.record_trade(trade)

    trades = await storage.get_recent_trades(symbol="BTCUSDT", limit=10)
    assert len(trades) == 1
    assert trades[0].symbol == "BTCUSDT"
    assert trades[0].price == 68200.0
    assert trades[0].quantity == 0.5
    assert trades[0].side == TradeSide.AGGRESSIVE_BUY
    assert trades[0].trade_id == "trade_1001"

    # 2. Probar Liquidation CRUD
    liq = LiquidationEvent(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        side=PositionSide.SHORT,
        price=69000.0,
        quantity=1.2,
        filled_quantity=1.2,
        usd_volume=82800.0,
        timestamp=now,
        origin=DataOrigin.OBSERVED,
    )
    await storage.record_liquidation(liq)

    liqs = await storage.get_recent_liquidations(symbol="BTCUSDT", limit=10)
    assert len(liqs) == 1
    assert liqs[0].symbol == "BTCUSDT"
    assert liqs[0].side == PositionSide.SHORT
    assert liqs[0].price == 69000.0
    assert liqs[0].usd_volume == 82800.0
    assert liqs[0].origin == DataOrigin.OBSERVED

    await storage.close()


@pytest.mark.asyncio
async def test_uninitialized_storage_raises_runtime_error() -> None:
    """Verifica que operar sobre una base de datos no inicializada lance RuntimeError."""
    storage = SqliteStorageRepository(database_path=":memory:")

    trade = Trade(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        price=68000.0,
        quantity=1.0,
        side=TradeSide.AGGRESSIVE_BUY,
    )
    liq = LiquidationEvent(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        price=68000.0,
        quantity=1.0,
        filled_quantity=1.0,
        usd_volume=68000.0,
    )

    with pytest.raises(RuntimeError):
        await storage.record_trade(trade)

    with pytest.raises(RuntimeError):
        await storage.record_liquidation(liq)

    with pytest.raises(RuntimeError):
        await storage.get_recent_trades("BTCUSDT")

    with pytest.raises(RuntimeError):
        await storage.get_recent_liquidations("BTCUSDT")


@pytest.mark.asyncio
async def test_sqlite_file_based_and_double_close(tmp_path: Path) -> None:
    """Verifica la creación de directorio en disco y llamada idempotente a close() (líneas 25 y 73)."""
    db_file = tmp_path / "subdir" / "test.db"
    storage = SqliteStorageRepository(database_path=db_file)
    await storage.initialize()
    assert db_file.exists()
    await storage.close()
    # Segundo close cuando self._db is None (línea 73->exit)
    await storage.close()


@pytest.mark.asyncio
async def test_sqlite_migration_legacy_rows_to_observed(tmp_path: Path) -> None:
    """Verifica que filas con orígenes legados ('real', 'estimated') se migren a 'observed' en initialize()."""
    import aiosqlite

    db_file = tmp_path / "legacy.db"

    # 1. Crear base de datos previa con filas legadas
    async with aiosqlite.connect(str(db_file)) as conn:
        await conn.execute("""
            CREATE TABLE liquidations (
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
        await conn.execute("""
            INSERT INTO liquidations (exchange, symbol, side, price, quantity, filled_quantity, usd_volume, timestamp, origin)
            VALUES ('binance', 'BTCUSDT', 'long', 68000.0, 1.0, 1.0, 68000.0, '2026-10-30T12:00:00Z', 'real'),
                   ('binance', 'BTCUSDT', 'short', 69000.0, 2.0, 2.0, 138000.0, '2026-10-30T12:01:00Z', 'estimated')
        """)
        await conn.commit()

    # 2. Inicializar repositorio LiqScope sobre la base de datos previa
    storage = SqliteStorageRepository(database_path=db_file)
    await storage.initialize()

    # 3. Recuperar liquidaciones y comprobar que fueron migradas a OBSERVED
    liqs = await storage.get_recent_liquidations(symbol="BTCUSDT", limit=10)
    assert len(liqs) == 2
    assert liqs[0].origin == DataOrigin.OBSERVED
    assert liqs[1].origin == DataOrigin.OBSERVED

    await storage.close()
