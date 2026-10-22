"""Tests unitarios para el repositorio SQLite de almacenamiento."""

from datetime import UTC, datetime

import pytest

from liqscope.models.common import DataOrigin, Exchange, PositionSide
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
        side=PositionSide.LONG,
        timestamp=now,
        trade_id="trade_1001",
    )
    await storage.record_trade(trade)

    trades = await storage.get_recent_trades(symbol="BTCUSDT", limit=10)
    assert len(trades) == 1
    assert trades[0].symbol == "BTCUSDT"
    assert trades[0].price == 68200.0
    assert trades[0].quantity == 0.5
    assert trades[0].side == PositionSide.LONG
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
        origin=DataOrigin.ESTIMATED,
    )
    await storage.record_liquidation(liq)

    liqs = await storage.get_recent_liquidations(symbol="BTCUSDT", limit=10)
    assert len(liqs) == 1
    assert liqs[0].symbol == "BTCUSDT"
    assert liqs[0].side == PositionSide.SHORT
    assert liqs[0].price == 69000.0
    assert liqs[0].usd_volume == 82800.0
    assert liqs[0].origin == DataOrigin.ESTIMATED

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
        side=PositionSide.LONG,
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
