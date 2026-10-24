"""Tests unitarios para modelos de dominio de mercado y liquidaciones."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from liqscope.models.common import DataCoverage, DataOrigin, Exchange, PositionSide, TradeSide
from liqscope.models.heatmap import (
    DEFAULT_DISCLAIMER,
    HeatmapBin,
    HeatmapSnapshot,
    LiquidationLevel,
)
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


def test_data_origin_and_coverage_case_insensitive() -> None:
    """Verifica que DataOrigin y DataCoverage admitan mayúsculas, minúsculas e invalidaciones."""
    assert DataOrigin("MODELED") == DataOrigin.MODELED
    assert DataOrigin("modeled") == DataOrigin.MODELED
    assert DataCoverage("NA") == DataCoverage.NA
    assert DataCoverage("na") == DataCoverage.NA

    with pytest.raises(ValueError):
        DataOrigin("invalid_origin")
    with pytest.raises(ValueError):
        DataOrigin(123)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        DataCoverage("invalid_coverage")
    with pytest.raises(ValueError):
        DataCoverage(123)  # type: ignore[arg-type]


def test_heatmap_models_defaults_and_validation() -> None:
    """Verifica los valores predeterminados y restricciones de los modelos del Heatmap."""
    level = LiquidationLevel(
        price=80000.0,
        volume_usd=500000.0,
        leverage=50.0,
        side=PositionSide.LONG,
    )
    assert level.origin == DataOrigin.MODELED

    bin_cell = HeatmapBin(
        price_min=80000.0,
        price_max=80050.0,
        price_mid=80025.0,
        estimated_volume_usd=500000.0,
    )
    assert bin_cell.origin == DataOrigin.MODELED
    assert bin_cell.coverage == DataCoverage.NA
    assert bin_cell.long_volume_usd == 0.0
    assert bin_cell.short_volume_usd == 0.0

    snapshot = HeatmapSnapshot(
        symbol="BTCUSDT",
        current_price=81500.0,
        bin_size=50.0,
        bins=[bin_cell],
        total_open_interest_usd=1000000.0,
        visible_bin_volume_usd=500000.0,
        coverage_pct=50.0,
    )
    assert snapshot.assumed_long_ratio == 0.50
    assert snapshot.source == "live"
    assert snapshot.disclaimer == DEFAULT_DISCLAIMER
    assert snapshot.is_complete is True

    # Validación de límites para coverage_pct y assumed_long_ratio
    with pytest.raises(ValidationError):
        HeatmapSnapshot(
            symbol="BTCUSDT",
            current_price=81500.0,
            bin_size=50.0,
            bins=[],
            coverage_pct=105.0,  # > 100
        )

    with pytest.raises(ValidationError):
        HeatmapSnapshot(
            symbol="BTCUSDT",
            current_price=81500.0,
            bin_size=50.0,
            bins=[],
            assumed_long_ratio=1.5,  # > 1.0
        )
