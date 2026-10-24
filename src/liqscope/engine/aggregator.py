"""Motor de agregación de niveles de liquidación en bins para el mapa de calor."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from liqscope.models.common import DataCoverage, DataOrigin, PositionSide
from liqscope.models.heatmap import (
    DEFAULT_DISCLAIMER,
    HeatmapBin,
    HeatmapSnapshot,
    LiquidationLevel,
)

# Escalones modelados de apalancamiento, MMR supuesto (MMR < 1/L) y peso predeterminado
MODELED_LEVERAGE_BRACKETS: list[tuple[float, float, float]] = [
    # (leverage, assumed_mmr, default_weight)
    (5.0, 0.040, 0.15),
    (10.0, 0.020, 0.25),
    (25.0, 0.010, 0.30),
    (50.0, 0.005, 0.20),
    (100.0, 0.004, 0.10),
]


def generate_liquidation_levels(
    mark_price: float,
    total_oi_usd: float,
    assumed_long_ratio: float = 0.50,
) -> list[LiquidationLevel]:
    """Genera los 10 niveles discretos de liquidación analítica para longs y shorts.

    Aplica los supuestos de MMR por escalón (MMR < 1/L) garantizando estrictamente
    los invariantes de dirección de precio: P_liq_long < P_mark < P_liq_short.
    """
    if mark_price <= 0 or total_oi_usd <= 0:
        return []

    levels: list[LiquidationLevel] = []
    long_total = total_oi_usd * assumed_long_ratio
    short_total = total_oi_usd * (1.0 - assumed_long_ratio)

    # 1. Proyectar Longs (P_liq < P_mark)
    if long_total > 0:
        for leverage, mmr, weight in MODELED_LEVERAGE_BRACKETS:
            delta = (1.0 / leverage) - mmr
            p_liq = mark_price * (1.0 - delta)
            vol = round(long_total * weight, 2)
            levels.append(
                LiquidationLevel(
                    price=round(p_liq, 2),
                    volume_usd=vol,
                    leverage=leverage,
                    side=PositionSide.LONG,
                    origin=DataOrigin.MODELED,
                )
            )

    # 2. Proyectar Shorts (P_liq > P_mark)
    if short_total > 0:
        for leverage, mmr, weight in reversed(MODELED_LEVERAGE_BRACKETS):
            delta = (1.0 / leverage) - mmr
            p_liq = mark_price * (1.0 + delta)
            vol = round(short_total * weight, 2)
            levels.append(
                LiquidationLevel(
                    price=round(p_liq, 2),
                    volume_usd=vol,
                    leverage=leverage,
                    side=PositionSide.SHORT,
                    origin=DataOrigin.MODELED,
                )
            )

    return levels


def build_heatmap_snapshot(
    symbol: str,
    mark_price: float,
    total_open_interest_usd: float,
    bin_size: float = 50.0,
    min_price: float | None = None,
    max_price: float | None = None,
    assumed_long_ratio: float = 0.50,
    source: str = "live",
) -> HeatmapSnapshot:
    """Construye un snapshot de mapa de calor en bins agregados con filtrado atómico por rango."""
    sym = symbol.upper()
    if mark_price <= 0:
        raise ValueError("mark_price debe ser mayor que cero")
    if total_open_interest_usd < 0:
        raise ValueError("total_open_interest_usd no puede ser negativo")

    if total_open_interest_usd == 0:
        return HeatmapSnapshot(
            symbol=sym,
            current_price=mark_price,
            timestamp=datetime.now(UTC),
            bin_size=bin_size,
            bins=[],
            total_open_interest_usd=0.0,
            visible_bin_volume_usd=0.0,
            coverage_pct=0.0,
            assumed_long_ratio=assumed_long_ratio,
            source=source,
            disclaimer=DEFAULT_DISCLAIMER,
            total_estimated_volume_usd=0.0,
            is_complete=True,
        )

    levels = generate_liquidation_levels(
        mark_price=mark_price,
        total_oi_usd=total_open_interest_usd,
        assumed_long_ratio=assumed_long_ratio,
    )

    # Agrupar niveles por índice de bin discreto
    binned_data: dict[int, dict[str, float]] = defaultdict(
        lambda: {"total": 0.0, "long": 0.0, "short": 0.0, "count": 0.0}
    )

    for lvl in levels:
        bin_idx = math.floor(lvl.price / bin_size)
        binned_data[bin_idx]["total"] += lvl.volume_usd
        if lvl.side == PositionSide.LONG:
            binned_data[bin_idx]["long"] += lvl.volume_usd
        else:
            binned_data[bin_idx]["short"] += lvl.volume_usd
        binned_data[bin_idx]["count"] += 1.0

    all_bins: list[HeatmapBin] = []
    for b_idx in sorted(binned_data.keys()):
        p_min = b_idx * bin_size
        p_max = p_min + bin_size
        p_mid = p_min + (bin_size / 2.0)
        entry = binned_data[b_idx]

        all_bins.append(
            HeatmapBin(
                price_min=round(p_min, 2),
                price_max=round(p_max, 2),
                price_mid=round(p_mid, 2),
                estimated_volume_usd=round(entry["total"], 2),
                long_volume_usd=round(entry["long"], 2),
                short_volume_usd=round(entry["short"], 2),
                estimated_positions=int(entry["count"]),
                origin=DataOrigin.MODELED,
                coverage=DataCoverage.NA,
            )
        )

    # Regla de inclusión atómica indivisible por solapamiento con [min_price, max_price]
    visible_bins: list[HeatmapBin] = [
        b
        for b in all_bins
        if (min_price is None or b.price_max > min_price)
        and (max_price is None or b.price_min < max_price)
    ]

    visible_volume = sum(b.estimated_volume_usd for b in visible_bins)
    coverage_pct = (
        (visible_volume / total_open_interest_usd) * 100.0 if total_open_interest_usd > 0 else 0.0
    )

    return HeatmapSnapshot(
        symbol=sym,
        current_price=mark_price,
        timestamp=datetime.now(UTC),
        bin_size=bin_size,
        bins=visible_bins,
        total_open_interest_usd=round(total_open_interest_usd, 2),
        visible_bin_volume_usd=round(visible_volume, 2),
        coverage_pct=round(coverage_pct, 6),
        assumed_long_ratio=assumed_long_ratio,
        source=source,
        disclaimer=DEFAULT_DISCLAIMER,
        total_estimated_volume_usd=round(visible_volume, 2),
        is_complete=True,
    )


class HeatmapAggregator:
    """Clase de conveniencia y compatibilidad con fases anteriores."""

    def __init__(
        self,
        config_path: Path | str = "config/default_distribution.yaml",
    ) -> None:
        self.config_path = Path(config_path)
        self.distribution_weights: dict[str, dict[float, float]] = self._load_distribution_config()

    def _load_distribution_config(self) -> dict[str, dict[float, float]]:
        """Carga los supuestos de distribución ponderada de apalancamientos desde YAML."""
        if not self.config_path.exists():
            default_weights = {
                5.0: 0.15,
                10.0: 0.25,
                25.0: 0.30,
                50.0: 0.20,
                100.0: 0.10,
            }
            return {"DEFAULT": default_weights}

        with open(self.config_path, encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        symbol_defaults = data.get("symbol_defaults", {})
        result: dict[str, dict[float, float]] = {}

        for sym, cfg in symbol_defaults.items():
            dist = cfg.get("leverage_distribution", {})
            result[sym.upper()] = {float(k): float(v) for k, v in dist.items()}

        if "DEFAULT" not in result:
            result["DEFAULT"] = {
                5.0: 0.15,
                10.0: 0.25,
                25.0: 0.30,
                50.0: 0.20,
                100.0: 0.10,
            }

        return result

    def get_leverage_weights_for_symbol(self, symbol: str) -> dict[float, float]:
        """Retorna el mapeo de apalancamientos a pesos para el símbolo solicitado."""
        sym = symbol.upper()
        return self.distribution_weights.get(sym, self.distribution_weights["DEFAULT"])

    def generate_liquidation_levels(
        self,
        symbol: str,
        current_price: float,
        total_open_interest_usd: float,
        long_ratio: float = 0.5,
    ) -> list[LiquidationLevel]:
        """Genera niveles discretos delegando en el cálculo analítico estandarizado."""
        return generate_liquidation_levels(
            mark_price=current_price,
            total_oi_usd=total_open_interest_usd,
            assumed_long_ratio=long_ratio,
        )

    def build_snapshot(
        self,
        symbol: str,
        current_price: float,
        total_open_interest_usd: float,
        bin_size: float = 50.0,
        long_ratio: float = 0.5,
    ) -> HeatmapSnapshot:
        """Construye un snapshot agrupado delegando en build_heatmap_snapshot."""
        return build_heatmap_snapshot(
            symbol=symbol,
            mark_price=current_price,
            total_open_interest_usd=total_open_interest_usd,
            bin_size=bin_size,
            assumed_long_ratio=long_ratio,
        )
