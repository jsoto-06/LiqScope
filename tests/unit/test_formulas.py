"""Tests unitarios para las fórmulas de liquidación, tiers y agregación del heatmap."""

from pathlib import Path

import pytest

from liqscope.engine.aggregator import HeatmapAggregator
from liqscope.engine.formulas import (
    calculate_approximate_liquidation_price,
    calculate_exact_tier_liquidation_price,
)
from liqscope.engine.tiers import get_tier_for_notional
from liqscope.models.common import PositionSide

# ==============================================================================
# 1. Casos a mano calculados analíticamente (MMR etiquetado como supuesto)
# ==============================================================================


def test_hand_calculated_long_btc_10x() -> None:
    """Caso 1 calculado a mano: Long BTC 10x.

    Supuesto de entrada:
      P_entry = 60,000.0 USD
      Apalancamiento = 10.0x (1/L = 0.10)
      MMR supuesto (Tier 1 Binance BTC): 0.004 (0.40%)
    Cálculo:
      P_liq = 60000 * (1 - 0.10 + 0.004) = 60000 * 0.904 = 54,240.0 USD
    """
    assumed_mmr = 0.004
    liq_p = calculate_approximate_liquidation_price(
        entry_price=60_000.0,
        leverage=10.0,
        side=PositionSide.LONG,
        maintenance_margin_rate=assumed_mmr,
    )
    assert liq_p == 54_240.0


def test_hand_calculated_short_btc_10x() -> None:
    """Caso 2 calculado a mano: Short BTC 10x.

    Supuesto de entrada:
      P_entry = 60,000.0 USD
      Apalancamiento = 10.0x (1/L = 0.10)
      MMR supuesto (Tier 1 Binance BTC): 0.004 (0.40%)
    Cálculo:
      P_liq = 60000 * (1 + 0.10 - 0.004) = 60000 * 1.096 = 65,760.0 USD
    """
    assumed_mmr = 0.004
    liq_p = calculate_approximate_liquidation_price(
        entry_price=60_000.0,
        leverage=10.0,
        side=PositionSide.SHORT,
        maintenance_margin_rate=assumed_mmr,
    )
    assert liq_p == 65_760.0


def test_hand_calculated_long_eth_25x() -> None:
    """Caso 3 calculado a mano: Long ETH 25x.

    Supuesto de entrada:
      P_entry = 3,000.0 USD
      Apalancamiento = 25.0x (1/L = 0.04)
      MMR supuesto (Tier 1 Binance ETH): 0.005 (0.50%)
    Cálculo:
      P_liq = 3000 * (1 - 0.04 + 0.005) = 3000 * 0.965 = 2,895.0 USD
    """
    assumed_mmr = 0.005
    liq_p = calculate_approximate_liquidation_price(
        entry_price=3_000.0,
        leverage=25.0,
        side=PositionSide.LONG,
        maintenance_margin_rate=assumed_mmr,
    )
    assert liq_p == 2_895.0


def test_hand_calculated_short_eth_25x() -> None:
    """Caso 4 calculado a mano: Short ETH 25x.

    Supuesto de entrada:
      P_entry = 3,000.0 USD
      Apalancamiento = 25.0x (1/L = 0.04)
      MMR supuesto (Tier 1 Binance ETH): 0.005 (0.50%)
    Cálculo:
      P_liq = 3000 * (1 + 0.04 - 0.005) = 3000 * 1.035 = 3,105.0 USD
    """
    assumed_mmr = 0.005
    liq_p = calculate_approximate_liquidation_price(
        entry_price=3_000.0,
        leverage=25.0,
        side=PositionSide.SHORT,
        maintenance_margin_rate=assumed_mmr,
    )
    assert liq_p == 3_105.0


def test_hand_calculated_high_leverage_100x() -> None:
    """Caso 5 calculado a mano: Long y Short con 100x en BTC.

    Supuesto de entrada:
      P_entry = 60,000.0 USD
      Apalancamiento = 100.0x (1/L = 0.01)
      MMR supuesto = 0.004
    Cálculo:
      Long:  60000 * (1 - 0.01 + 0.004) = 60000 * 0.994 = 59,640.0 USD
      Short: 60000 * (1 + 0.01 - 0.004) = 60000 * 1.006 = 60,360.0 USD
    """
    assumed_mmr = 0.004
    liq_long = calculate_approximate_liquidation_price(
        60_000.0, 100.0, PositionSide.LONG, assumed_mmr
    )
    liq_short = calculate_approximate_liquidation_price(
        60_000.0, 100.0, PositionSide.SHORT, assumed_mmr
    )

    assert liq_long == 59_640.0
    assert liq_short == 60_360.0


def test_hand_calculated_exact_tier_formula() -> None:
    """Caso 6 calculado a mano: Fórmula exacta con deducción acumulada de tier (cum).

    Supuesto de entrada:
      P_entry = 60,000.0 USD
      Apalancamiento = 10.0x (1/L = 0.10)
      Cantidad Q = 2.0 BTC
      Nocional = 120,000 USDT -> Tier 2 (MMR supuesto = 0.005, cum supuesto = 50.0 USDT)
    Cálculo exacto:
      Numerador = 60000 * (1 - 0.10) + (50 / 2) = 54000 + 25 = 54025.0
      Denominador = 1 - 0.005 = 0.995
      P_liq = 54025 / 0.995 = 54,296.4824 USD
    """
    assumed_mmr = 0.005
    assumed_cum = 50.0

    liq_exact_long = calculate_exact_tier_liquidation_price(
        entry_price=60_000.0,
        leverage=10.0,
        side=PositionSide.LONG,
        maintenance_margin_rate=assumed_mmr,
        cum_maintenance_amount=assumed_cum,
        quantity=2.0,
    )
    assert liq_exact_long == 54_296.4824

    # Probar Short exacto
    liq_exact_short = calculate_exact_tier_liquidation_price(
        entry_price=60_000.0,
        leverage=10.0,
        side=PositionSide.SHORT,
        maintenance_margin_rate=assumed_mmr,
        cum_maintenance_amount=assumed_cum,
        quantity=2.0,
    )
    # Numerador: 60000 * (1 + 0.10) - (50 / 2) = 66000 - 25 = 65975.0
    # Denominador: 1 + 0.005 = 1.005
    # P_liq = 65975 / 1.005 = 65,646.7662
    assert liq_exact_short == 65_646.7662


# ==============================================================================
# 2. Validación de parámetros inválidos en fórmulas
# ==============================================================================


@pytest.mark.parametrize("invalid_p", [0.0, -100.0])
def test_formulas_invalid_entry_price(invalid_p: float) -> None:
    """Verifica que precios de entrada no positivos lancen ValueError."""
    with pytest.raises(ValueError):
        calculate_approximate_liquidation_price(invalid_p, 10.0, PositionSide.LONG, 0.004)


@pytest.mark.parametrize("invalid_lev", [0.5, 0.0, -5.0])
def test_formulas_invalid_leverage(invalid_lev: float) -> None:
    """Verifica que apalancamientos menores a 1.0 lancen ValueError."""
    with pytest.raises(ValueError):
        calculate_approximate_liquidation_price(60_000.0, invalid_lev, PositionSide.LONG, 0.004)


def test_formulas_invalid_mmr() -> None:
    """Verifica que un MMR negativo lance ValueError."""
    with pytest.raises(ValueError):
        calculate_approximate_liquidation_price(60_000.0, 10.0, PositionSide.LONG, -0.01)


def test_formulas_invalid_side() -> None:
    """Verifica que lados no direccionales como BOTH lancen ValueError."""
    with pytest.raises(ValueError):
        calculate_approximate_liquidation_price(60_000.0, 10.0, PositionSide.BOTH, 0.004)

    with pytest.raises(ValueError):
        calculate_exact_tier_liquidation_price(60_000.0, 10.0, PositionSide.BOTH, 0.004)


@pytest.mark.parametrize(
    ("p", "lev", "qty"),
    [
        (0.0, 10.0, 1.0),
        (-10.0, 10.0, 1.0),
        (60_000.0, 0.5, 1.0),
        (60_000.0, 10.0, 0.0),
        (60_000.0, 10.0, -1.0),
    ],
)
def test_exact_tier_formula_invalid_inputs(p: float, lev: float, qty: float) -> None:
    """Verifica que parámetros inválidos en cálculo exacto lancen ValueError."""
    with pytest.raises(ValueError):
        calculate_exact_tier_liquidation_price(p, lev, PositionSide.LONG, 0.005, quantity=qty)


def test_binance_eth_tier_lookup() -> None:
    """Verifica la asignación de escalones para ETHUSDT con estatus PENDING_VERIFICATION."""
    t1 = get_tier_for_notional("ETHUSDT", 10_000.0)
    assert t1.tier == 1
    assert t1.maintenance_margin_rate == 0.005
    assert t1.status == "PENDING_VERIFICATION"

    t2 = get_tier_for_notional("ETHUSDT", 50_000.0)
    assert t2.tier == 2
    assert t2.maintenance_margin_rate == 0.010
    assert t2.status == "PENDING_VERIFICATION"

    t4 = get_tier_for_notional("ETHUSDT", 1_000_000.0)
    assert t4.tier == 4
    assert t4.status == "PENDING_VERIFICATION"


def test_aggregator_zero_inputs_returns_empty() -> None:
    """Verifica que entradas con OI o precio <= 0 retornen lista vacía."""
    aggregator = HeatmapAggregator()
    assert aggregator.generate_liquidation_levels("BTCUSDT", 0.0, 1_000_000.0) == []
    assert aggregator.generate_liquidation_levels("BTCUSDT", 60_000.0, 0.0) == []


# ==============================================================================
# 3. Verificación de Tiers oficiales y etiquetado PENDING_VERIFICATION
# ==============================================================================


def test_binance_btc_tier_lookup() -> None:
    """Verifica la asignación de escalones para BTCUSDT con estatus PENDING_VERIFICATION."""
    # Nocional pequeño
    t1 = get_tier_for_notional("BTCUSDT", 25_000.0)
    assert t1.tier == 1
    assert t1.maintenance_margin_rate == 0.004
    assert t1.status == "PENDING_VERIFICATION"
    assert "binance.com" in t1.official_url
    assert t1.consulted_at == "2026-10-22"

    # Nocional tramo institucional (> 5M USDT, pendiente de verificación dinámica)
    t5 = get_tier_for_notional("BTCUSDT", 10_000_000.0)
    assert t5.tier == 5
    assert t5.status == "PENDING_VERIFICATION"


def test_unsupported_symbol_returns_pending_verification() -> None:
    """Verifica que pares fuera del alcance de Fase 2 queden marcados como PENDING_VERIFICATION."""
    tier = get_tier_for_notional("SOLUSDT", 50_000.0)
    assert tier.status == "PENDING_VERIFICATION"


# ==============================================================================
# 4. Tests de conservación de volumen en agregación del Heatmap
# ==============================================================================


def test_heatmap_volume_conservation() -> None:
    """Verifica rigurosamente que la suma de los bins conserve el volumen total de entrada."""
    aggregator = HeatmapAggregator()
    total_oi_usd = 10_000_000.0  # 10M USD
    current_price = 68_000.0

    snapshot = aggregator.build_snapshot(
        symbol="BTCUSDT",
        current_price=current_price,
        total_open_interest_usd=total_oi_usd,
        bin_size=50.0,
        long_ratio=0.5,
    )

    assert len(snapshot.bins) > 0
    # La suma de todos los bins debe coincidir con el volumen total de entrada (margen de redondeo < 1 USD)
    sum_binned_volume = sum(b.estimated_volume_usd for b in snapshot.bins)
    assert abs(sum_binned_volume - total_oi_usd) < 1.0

    # Cada bin individual debe conservar que total == long + short
    for b in snapshot.bins:
        assert abs(b.estimated_volume_usd - (b.long_volume_usd + b.short_volume_usd)) < 0.05


def test_exact_tier_formula_invalid_denominator() -> None:
    """Verifica que un MMR >= 1.0 en LONG genere un denominador no positivo y lance ValueError (línea 90)."""
    with pytest.raises(ValueError, match="Denominador inválido"):
        calculate_exact_tier_liquidation_price(
            entry_price=60_000.0,
            leverage=10.0,
            side=PositionSide.LONG,
            maintenance_margin_rate=1.0,
            cum_maintenance_amount=0.0,
            quantity=1.0,
        )


def test_get_tier_for_notional_fallback_last_tier() -> None:
    """Verifica que un nocional infinito o fuera de rango alcance el fallback return tiers[-1] (línea 170)."""
    tier = get_tier_for_notional("BTCUSDT", float("inf"))
    assert tier.tier == 5
    assert tier.status == "PENDING_VERIFICATION"


def test_aggregator_missing_config_file_uses_fallback(tmp_path: Path) -> None:
    """Verifica el fallback por defecto si el archivo YAML no existe (líneas 31-32)."""
    non_existent = tmp_path / "does_not_exist.yaml"
    agg = HeatmapAggregator(config_path=non_existent)
    weights = agg.get_leverage_weights_for_symbol("BTCUSDT")
    assert weights[5.0] == 0.15
    assert weights[100.0] == 0.10
    assert "DEFAULT" in agg.distribution_weights


def test_aggregator_config_without_default_key(tmp_path: Path) -> None:
    """Verifica que si el YAML carece de clave DEFAULT, se inyecte el fallback predeterminado (línea 45)."""
    cfg_file = tmp_path / "custom.yaml"
    cfg_file.write_text(
        "symbol_defaults:\n  CUSTOM:\n    leverage_distribution:\n      10.0: 1.0\n",
        encoding="utf-8",
    )
    agg = HeatmapAggregator(config_path=cfg_file)
    assert "DEFAULT" in agg.distribution_weights
    assert agg.distribution_weights["DEFAULT"][10.0] == 0.25
    assert agg.distribution_weights["CUSTOM"][10.0] == 1.0


def test_aggregator_extreme_long_ratios() -> None:
    """Verifica el cálculo cuando long_ratio es 0.0 (solo shorts) y 1.0 (solo longs) (líneas 74->93 y 94->71)."""
    aggregator = HeatmapAggregator()
    # long_ratio = 0.0 (long_volume <= 0 -> salta línea 74 a 93)
    levels_all_short = aggregator.generate_liquidation_levels(
        "BTCUSDT", current_price=60_000.0, total_open_interest_usd=100_000.0, long_ratio=0.0
    )
    assert len(levels_all_short) > 0
    assert all(lvl.side == PositionSide.SHORT for lvl in levels_all_short)

    # long_ratio = 1.0 (short_volume <= 0 -> salta línea 94 a fin de iteración)
    levels_all_long = aggregator.generate_liquidation_levels(
        "BTCUSDT", current_price=60_000.0, total_open_interest_usd=100_000.0, long_ratio=1.0
    )
    assert len(levels_all_long) > 0
    assert all(lvl.side == PositionSide.LONG for lvl in levels_all_long)
