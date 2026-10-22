"""Tests unitarios para modelos de dominio de mercado y liquidaciones."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from liqscope.models.common import DataOrigin, Exchange, PositionSide, TradeSide
from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import OpenInterestSnapshot, Trade


def test_trade_model_valid() -> None:
    """Verifica la creación y validación de una instancia de Trade."""
    now = datetime.now(UTC)
    trade = Trade(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        price=68000.5,
        quantity=0.25,
        side=TradeSide.AGGRESSIVE_BUY,
        timestamp=now,
        trade_id="123456",
    )
    assert trade.exchange == Exchange.BINANCE
    assert trade.symbol == "BTCUSDT"
    assert trade.price == 68000.5
    assert trade.quantity == 0.25
    assert trade.side == TradeSide.AGGRESSIVE_BUY
    assert trade.timestamp == now
    assert trade.trade_id == "123456"


@pytest.mark.parametrize("invalid_price", [0, -100.0])
def test_trade_model_invalid_price(invalid_price: float) -> None:
    """Verifica que precios menores o iguales a cero lancen ValidationError."""
    with pytest.raises(ValidationError):
        Trade(
            exchange=Exchange.BINANCE,
            symbol="BTCUSDT",
            price=invalid_price,
            quantity=1.0,
            side=TradeSide.AGGRESSIVE_BUY,
        )


@pytest.mark.parametrize("invalid_qty", [0, -0.5])
def test_trade_model_invalid_quantity(invalid_qty: float) -> None:
    """Verifica que cantidades menores o iguales a cero lancen ValidationError."""
    with pytest.raises(ValidationError):
        Trade(
            exchange=Exchange.BINANCE,
            symbol="BTCUSDT",
            price=68000.0,
            quantity=invalid_qty,
            side=TradeSide.AGGRESSIVE_BUY,
        )


def test_liquidation_event_model_valid() -> None:
    """Verifica la creación de un LiquidationEvent válido."""
    now = datetime.now(UTC)
    liq = LiquidationEvent(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        side=PositionSide.LONG,
        price=67500.0,
        quantity=1.5,
        filled_quantity=1.5,
        usd_volume=101250.0,
        timestamp=now,
        origin=DataOrigin.ESTIMATED,
    )
    assert liq.exchange == Exchange.BINANCE
    assert liq.symbol == "BTCUSDT"
    assert liq.side == PositionSide.LONG
    assert liq.usd_volume == 101250.0
    assert liq.origin == DataOrigin.ESTIMATED


def test_open_interest_snapshot_valid() -> None:
    """Verifica la creación de un OpenInterestSnapshot válido."""
    oi = OpenInterestSnapshot(
        exchange=Exchange.BINANCE,
        symbol="BTCUSDT",
        open_interest=35000.5,
    )
    assert oi.open_interest == 35000.5
    assert oi.symbol == "BTCUSDT"
