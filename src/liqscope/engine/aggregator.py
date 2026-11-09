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

# Perfiles cuantitativos de acumulación por horizonte temporal LiqScope
TIMEFRAME_PROFILES: dict[str, dict[str, Any]] = {
    "12h": {
        "name": "12 Horas",
        "description": "Scalping ultra-corto plazo (predominio 50x-100x)",
        "leverage_brackets": [
            (10.0, 0.020, 0.05),
            (25.0, 0.010, 0.20),
            (50.0, 0.005, 0.40),
            (100.0, 0.004, 0.35),
        ],
        "entry_offsets": [0.0, 0.003, -0.003],
        "offset_weights": [0.60, 0.20, 0.20],
        "oi_factor": 0.45,
    },
    "24h": {
        "name": "24 Horas",
        "description": "Intradía diario (predominio 25x-50x)",
        "leverage_brackets": [
            (5.0, 0.040, 0.03),
            (10.0, 0.020, 0.12),
            (25.0, 0.010, 0.30),
            (50.0, 0.005, 0.35),
            (100.0, 0.004, 0.20),
        ],
        "entry_offsets": [0.0, 0.006, -0.006, 0.012, -0.012],
        "offset_weights": [0.44, 0.20, 0.20, 0.08, 0.08],
        "oi_factor": 0.65,
    },
    "3d": {
        "name": "3 Días",
        "description": "Táctico corto plazo (predominio 25x-50x)",
        "leverage_brackets": [
            (5.0, 0.040, 0.10),
            (10.0, 0.020, 0.20),
            (25.0, 0.010, 0.35),
            (50.0, 0.005, 0.25),
            (100.0, 0.004, 0.10),
        ],
        "entry_offsets": [0.0, 0.012, -0.012, 0.025, -0.025],
        "offset_weights": [0.36, 0.22, 0.22, 0.10, 0.10],
        "oi_factor": 0.80,
    },
    "1w": {
        "name": "1 Semana",
        "description": "Swing trading semanal (predominio 10x-25x)",
        "leverage_brackets": [
            (5.0, 0.040, 0.18),
            (10.0, 0.020, 0.32),
            (25.0, 0.010, 0.35),
            (50.0, 0.005, 0.12),
            (100.0, 0.004, 0.03),
        ],
        "entry_offsets": [0.0, 0.020, -0.020, 0.040, -0.040, 0.070, -0.070],
        "offset_weights": [0.28, 0.18, 0.18, 0.12, 0.12, 0.06, 0.06],
        "oi_factor": 0.90,
    },
    "1m": {
        "name": "1 Mes",
        "description": "Posicionamiento mensual (predominio 5x-10x)",
        "leverage_brackets": [
            (5.0, 0.040, 0.28),
            (10.0, 0.020, 0.40),
            (25.0, 0.010, 0.24),
            (50.0, 0.005, 0.07),
            (100.0, 0.004, 0.01),
        ],
        "entry_offsets": [0.0, 0.035, -0.035, 0.070, -0.070, 0.120, -0.120],
        "offset_weights": [0.22, 0.18, 0.18, 0.13, 0.13, 0.08, 0.08],
        "oi_factor": 0.98,
    },
    "3m": {
        "name": "3 Meses",
        "description": "Macro-estructural trimestral (predominio 5x-10x institucional)",
        "leverage_brackets": [
            (5.0, 0.040, 0.38),
            (10.0, 0.020, 0.42),
            (25.0, 0.010, 0.16),
            (50.0, 0.005, 0.04),
        ],
        "entry_offsets": [0.0, 0.060, -0.060, 0.120, -0.120, 0.200, -0.200],
        "offset_weights": [0.22, 0.18, 0.18, 0.14, 0.14, 0.07, 0.07],
        "oi_factor": 1.00,
    },
}


def generate_liquidation_levels(
    mark_price: float,
    total_oi_usd: float,
    assumed_long_ratio: float = 0.50,
    timeframe: str = "24h",
) -> list[LiquidationLevel]:
    """Genera los niveles discretos de liquidación analítica para longs y shorts
    según el horizonte temporal LiqScope seleccionado.

    Aplica los supuestos de MMR por escalón (MMR < 1/L) garantizando estrictamente
    los invariantes de dirección de precio: P_liq_long < P_mark < P_liq_short y
    filtrando posiciones liquidadas previamente mediante purga de supervivencia.
    """
    if mark_price <= 0 or total_oi_usd <= 0:
        return []

    profile = TIMEFRAME_PROFILES.get(timeframe.lower().strip(), TIMEFRAME_PROFILES["24h"])
    leverage_brackets = profile["leverage_brackets"]
    entry_offsets = profile.get("entry_offsets", [0.0])
    offset_weights = profile.get("offset_weights", [1.0])
    oi_factor = profile.get("oi_factor", 1.0)

    effective_oi = total_oi_usd * oi_factor
    long_total = effective_oi * assumed_long_ratio
    short_total = effective_oi * (1.0 - assumed_long_ratio)

    levels: list[LiquidationLevel] = []

    # 1. Proyectar Longs (P_liq < P_mark)
    if long_total > 0:
        for offset, o_weight in zip(entry_offsets, offset_weights, strict=False):
            p_entry = mark_price * (1.0 + offset)
            for leverage, mmr, lev_weight in leverage_brackets:
                delta = (1.0 / leverage) - mmr
                p_liq = p_entry * (1.0 - delta)
                # Invariante estricto y purga de posiciones ya liquidadas en el pasado
                if p_liq >= mark_price:
                    continue
                vol = round(long_total * lev_weight * o_weight, 2)
                if vol > 0:
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
        for offset, o_weight in zip(entry_offsets, offset_weights, strict=False):
            p_entry = mark_price * (1.0 + offset)
            for leverage, mmr, lev_weight in reversed(leverage_brackets):
                delta = (1.0 / leverage) - mmr
                p_liq = p_entry * (1.0 + delta)
                # Invariante estricto y purga de posiciones ya liquidadas en el pasado
                if p_liq <= mark_price:
                    continue
                vol = round(short_total * lev_weight * o_weight, 2)
                if vol > 0:
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
    cached: bool = False,
    data_age_sec: float = 0.0,
    long_account_ratio: float = 0.50,
    short_account_ratio: float = 0.50,
    ratio_source: str = "live",
    exchange: str = "all",
    exchange_breakdown: dict[str, float] | None = None,
    timeframe: str = "24h",
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
            long_account_ratio=long_account_ratio,
            short_account_ratio=short_account_ratio,
            ratio_source=ratio_source,
            exchange=exchange,
            exchange_breakdown=exchange_breakdown or {},
            timeframe=timeframe,
        )

    levels = generate_liquidation_levels(
        mark_price=mark_price,
        total_oi_usd=total_open_interest_usd,
        assumed_long_ratio=assumed_long_ratio,
        timeframe=timeframe,
    )

    # Agrupar niveles por índice de bin discreto
    binned_data: dict[int, dict[str, Any]] = defaultdict(
        lambda: {
            "total": 0.0,
            "long": 0.0,
            "short": 0.0,
            "count": 0.0,
            "lev_vols": defaultdict(float),
        }
    )

    for lvl in levels:
        bin_idx = math.floor(lvl.price / bin_size)
        binned_data[bin_idx]["total"] += lvl.volume_usd
        if lvl.side == PositionSide.LONG:
            binned_data[bin_idx]["long"] += lvl.volume_usd
        else:
            binned_data[bin_idx]["short"] += lvl.volume_usd
        binned_data[bin_idx]["count"] += 1.0
        binned_data[bin_idx]["lev_vols"][lvl.leverage] += lvl.volume_usd

    all_bins: list[HeatmapBin] = []
    for b_idx in sorted(binned_data.keys()):
        p_min = b_idx * bin_size
        p_max = p_min + bin_size
        p_mid = p_min + (bin_size / 2.0)
        entry = binned_data[b_idx]
        lev_map: dict[float, float] = entry["lev_vols"]
        leverages_list = sorted(lev_map.keys())
        dominant_leverage = max(lev_map.items(), key=lambda x: x[1])[0] if lev_map else None

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
                dominant_leverage=dominant_leverage,
                leverages=leverages_list,
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
        cached=cached,
        data_age_sec=round(data_age_sec, 2),
        total_estimated_volume_usd=round(visible_volume, 2),
        is_complete=True,
        long_account_ratio=round(long_account_ratio, 4),
        short_account_ratio=round(short_account_ratio, 4),
        ratio_source=ratio_source,
        exchange=exchange,
        exchange_breakdown=exchange_breakdown or {},
        timeframe=timeframe,
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
            long_account_ratio=long_ratio,
            short_account_ratio=round(1.0 - long_ratio, 4),
        )
