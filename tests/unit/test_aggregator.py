"""Pruebas unitarias de invariantes y agregación del modelo de mapa de calor (Fase 4)."""

from __future__ import annotations

import pytest

from liqscope.engine.aggregator import (
    HeatmapAggregator,
    build_heatmap_snapshot,
    generate_liquidation_levels,
)
from liqscope.models.common import DataOrigin, PositionSide

P_MARK = 81498.90
OI_BTC = 95448.751
TOTAL_OI_USD = round(OI_BTC * P_MARK, 2)  # 7,778,968,212.87 USD
ASSUMED_LONG_RATIO = 0.50
BIN_SIZE = 50.0


def test_invariants_directional_prices() -> None:
    """Invariante 1: P_liq_long < P_mark < P_liq_short para todos los apalancamientos."""
    levels = generate_liquidation_levels(
        mark_price=P_MARK,
        total_oi_usd=TOTAL_OI_USD,
        assumed_long_ratio=ASSUMED_LONG_RATIO,
    )
    assert len(levels) == 10

    long_levels = [lvl for lvl in levels if lvl.side == PositionSide.LONG]
    short_levels = [lvl for lvl in levels if lvl.side == PositionSide.SHORT]

    assert len(long_levels) == 5
    assert len(short_levels) == 5

    for lvl in long_levels:
        assert lvl.price < P_MARK, f"Infracción Long: {lvl.price} >= {P_MARK} (lev={lvl.leverage})"

    for lvl in short_levels:
        assert lvl.price > P_MARK, f"Infracción Short: {lvl.price} <= {P_MARK} (lev={lvl.leverage})"


def test_invariants_volume_sums_and_symmetry_without_filter() -> None:
    """Invariante 2: Sin filtro de rango, la suma coincide con Total OI y hay simetría."""
    snapshot = build_heatmap_snapshot(
        symbol="BTCUSDT",
        mark_price=P_MARK,
        total_open_interest_usd=TOTAL_OI_USD,
        bin_size=BIN_SIZE,
        min_price=None,
        max_price=None,
        assumed_long_ratio=ASSUMED_LONG_RATIO,
    )

    long_sum = sum(b.long_volume_usd for b in snapshot.bins)
    short_sum = sum(b.short_volume_usd for b in snapshot.bins)
    visible_sum = sum(b.estimated_volume_usd for b in snapshot.bins)

    expected_long_usd = TOTAL_OI_USD * ASSUMED_LONG_RATIO
    expected_short_usd = TOTAL_OI_USD * (1.0 - ASSUMED_LONG_RATIO)

    # Simetría estricta de totales (tolerancia explícita 0.01 USD)
    assert long_sum == pytest.approx(expected_long_usd, abs=0.01)
    assert short_sum == pytest.approx(expected_short_usd, abs=0.01)
    assert long_sum == pytest.approx(short_sum, abs=0.01)

    # Consistencia de volumen visible y cobertura al 100%
    # Nota: la suma de 10 bins discretos redondeados individualmente a centavos difiere en
    # exactamente 0.01 USD respecto al total impar (7,778,968,212.87 frente a .88).
    # En IEEE 754 float64, 7778968212.88 - 7778968212.87 = 0.0100002288...
    # Por tanto, se utiliza tolerancia de 0.02 USD para absorber la precisión binaria.
    assert visible_sum == pytest.approx(TOTAL_OI_USD, abs=0.02)
    assert snapshot.visible_bin_volume_usd == pytest.approx(TOTAL_OI_USD, abs=0.02)
    assert snapshot.coverage_pct == pytest.approx(100.0, abs=0.01)


def test_invariants_filtered_coverage_and_atomic_bins() -> None:
    """Invariante 3: Con filtro [79000, 83000], coverage_pct = 45.0% y bins atómicos."""
    min_price = 79000.0
    max_price = 83000.0

    snapshot = build_heatmap_snapshot(
        symbol="BTCUSDT",
        mark_price=P_MARK,
        total_open_interest_usd=TOTAL_OI_USD,
        bin_size=BIN_SIZE,
        min_price=min_price,
        max_price=max_price,
        assumed_long_ratio=ASSUMED_LONG_RATIO,
    )

    # Contiene exactamente 5 bins (25x L, 50x L, 100x L, 100x S, 50x S)
    assert len(snapshot.bins) == 5

    # Regla atómica: cada bin visible cumple b.price_max > min_price y b.price_min < max_price
    for b in snapshot.bins:
        assert b.price_max > min_price
        assert b.price_min < max_price
        assert b.origin == DataOrigin.MODELED

    visible_sum = sum(b.estimated_volume_usd for b in snapshot.bins)
    expected_sum = 3500535695.79  # 45% exacto de 7,778,968,212.87

    assert visible_sum == pytest.approx(expected_sum, abs=0.01)
    assert snapshot.visible_bin_volume_usd == pytest.approx(expected_sum, abs=0.01)

    expected_coverage = (visible_sum / TOTAL_OI_USD) * 100.0
    assert snapshot.coverage_pct == pytest.approx(45.0, abs=0.01)
    assert snapshot.coverage_pct == pytest.approx(expected_coverage, abs=0.01)


def test_aggregator_zero_or_negative_inputs() -> None:
    """Verifica el comportamiento seguro con precios o OI menores o iguales a cero."""
    assert generate_liquidation_levels(mark_price=0.0, total_oi_usd=1000.0) == []
    assert generate_liquidation_levels(mark_price=80000.0, total_oi_usd=0.0) == []
    assert generate_liquidation_levels(mark_price=-100.0, total_oi_usd=-500.0) == []

    with pytest.raises(ValueError, match="mark_price"):
        build_heatmap_snapshot(
            symbol="BTCUSDT",
            mark_price=0.0,
            total_open_interest_usd=1000.0,
        )

    with pytest.raises(ValueError, match="total_open_interest_usd"):
        build_heatmap_snapshot(
            symbol="BTCUSDT",
            mark_price=80000.0,
            total_open_interest_usd=-10.0,
        )

    snap_zero_oi = build_heatmap_snapshot(
        symbol="BTCUSDT",
        mark_price=80000.0,
        total_open_interest_usd=0.0,
    )
    assert snap_zero_oi.bins == []
    assert snap_zero_oi.visible_bin_volume_usd == 0.0
    assert snap_zero_oi.coverage_pct == 0.0


def test_atomic_bin_boundary_overlap() -> None:
    """Verifica la regla de frontera estricta: b.price_max > min y b.price_min < max."""
    # En nuestro cálculo para BTCUSDT, el bin de 100x L es [81000.0, 81050.0)
    # Si min_price = 81050.0, b.price_max (81050.0) > 81050.0 es False -> se descarta
    snap_boundary = build_heatmap_snapshot(
        symbol="BTCUSDT",
        mark_price=P_MARK,
        total_open_interest_usd=TOTAL_OI_USD,
        bin_size=BIN_SIZE,
        min_price=81050.0,
        max_price=81050.0,
    )
    assert snap_boundary.bins == []
    assert snap_boundary.visible_bin_volume_usd == 0.0


def test_heatmap_aggregator_class_compatibility() -> None:
    """Verifica que HeatmapAggregator delegue correctamente y mantenga compatibilidad."""
    agg = HeatmapAggregator()
    levels = agg.generate_liquidation_levels(
        symbol="BTCUSDT",
        current_price=P_MARK,
        total_open_interest_usd=TOTAL_OI_USD,
        long_ratio=0.5,
    )
    assert len(levels) == 10

    snap = agg.build_snapshot(
        symbol="BTCUSDT",
        current_price=P_MARK,
        total_open_interest_usd=TOTAL_OI_USD,
        bin_size=50.0,
        long_ratio=0.5,
    )
    assert len(snap.bins) == 10
    assert snap.visible_bin_volume_usd == pytest.approx(TOTAL_OI_USD, abs=0.02)
