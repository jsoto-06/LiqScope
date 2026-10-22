"""Motor de agregación de niveles de liquidación en bins para el mapa de calor."""

import math
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from liqscope.engine.formulas import calculate_approximate_liquidation_price
from liqscope.engine.tiers import get_tier_for_notional
from liqscope.models.common import DataOrigin, PositionSide
from liqscope.models.heatmap import HeatmapBin, HeatmapSnapshot, LiquidationLevel


class HeatmapAggregator:
    """Calcula y agrega zonas de liquidación estimadas a partir de Open Interest y apalancamientos."""

    def __init__(
        self,
        config_path: Path | str = "config/default_distribution.yaml",
    ) -> None:
        self.config_path = Path(config_path)
        self.distribution_weights: dict[str, dict[float, float]] = self._load_distribution_config()

    def _load_distribution_config(self) -> dict[str, dict[float, float]]:
        """Carga los supuestos de distribución ponderada de apalancamientos desde YAML."""
        if not self.config_path.exists():
            # Fallback seguro predeterminado
            default_weights = {5.0: 0.15, 10.0: 0.25, 25.0: 0.30, 50.0: 0.20, 100.0: 0.10}
            return {"DEFAULT": default_weights}

        with open(self.config_path, encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

        symbol_defaults = data.get("symbol_defaults", {})
        result: dict[str, dict[float, float]] = {}

        for sym, cfg in symbol_defaults.items():
            dist = cfg.get("leverage_distribution", {})
            result[sym.upper()] = {float(k): float(v) for k, v in dist.items()}

        if "DEFAULT" not in result:
            result["DEFAULT"] = {5.0: 0.15, 10.0: 0.25, 25.0: 0.30, 50.0: 0.20, 100.0: 0.10}

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
        """Genera los niveles discretos de liquidación estimados para longs y shorts."""
        if total_open_interest_usd <= 0 or current_price <= 0:
            return []

        weights = self.get_leverage_weights_for_symbol(symbol)
        levels: list[LiquidationLevel] = []

        long_total_usd = total_open_interest_usd * long_ratio
        short_total_usd = total_open_interest_usd * (1.0 - long_ratio)

        for leverage, weight in weights.items():
            # 1. Proyectar Longs
            long_volume = long_total_usd * weight
            if long_volume > 0:
                tier = get_tier_for_notional(symbol, long_volume)
                liq_p = calculate_approximate_liquidation_price(
                    entry_price=current_price,
                    leverage=leverage,
                    side=PositionSide.LONG,
                    maintenance_margin_rate=tier.maintenance_margin_rate,
                )
                levels.append(
                    LiquidationLevel(
                        price=liq_p,
                        volume_usd=round(long_volume, 2),
                        leverage=leverage,
                        side=PositionSide.LONG,
                        origin=DataOrigin.ESTIMATED,
                    )
                )

            # 2. Proyectar Shorts
            short_volume = short_total_usd * weight
            if short_volume > 0:
                tier = get_tier_for_notional(symbol, short_volume)
                liq_p = calculate_approximate_liquidation_price(
                    entry_price=current_price,
                    leverage=leverage,
                    side=PositionSide.SHORT,
                    maintenance_margin_rate=tier.maintenance_margin_rate,
                )
                levels.append(
                    LiquidationLevel(
                        price=liq_p,
                        volume_usd=round(short_volume, 2),
                        leverage=leverage,
                        side=PositionSide.SHORT,
                        origin=DataOrigin.ESTIMATED,
                    )
                )

        return levels

    def build_snapshot(
        self,
        symbol: str,
        current_price: float,
        total_open_interest_usd: float,
        bin_size: float = 50.0,
        long_ratio: float = 0.5,
    ) -> HeatmapSnapshot:
        """Construye un snapshot agrupado en bins de precio conservando el volumen total."""
        sym = symbol.upper()
        levels = self.generate_liquidation_levels(
            symbol=sym,
            current_price=current_price,
            total_open_interest_usd=total_open_interest_usd,
            long_ratio=long_ratio,
        )

        # Agrupar niveles por índice de bin
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

        bins: list[HeatmapBin] = []
        for b_idx in sorted(binned_data.keys()):
            p_min = b_idx * bin_size
            p_max = p_min + bin_size
            p_mid = p_min + (bin_size / 2.0)
            entry = binned_data[b_idx]

            bins.append(
                HeatmapBin(
                    price_min=round(p_min, 2),
                    price_max=round(p_max, 2),
                    price_mid=round(p_mid, 2),
                    estimated_volume_usd=round(entry["total"], 2),
                    long_volume_usd=round(entry["long"], 2),
                    short_volume_usd=round(entry["short"], 2),
                    estimated_positions=int(entry["count"]),
                    origin=DataOrigin.ESTIMATED,
                )
            )

        total_volume = sum(b.estimated_volume_usd for b in bins)

        return HeatmapSnapshot(
            symbol=sym,
            current_price=current_price,
            timestamp=datetime.now(UTC),
            bin_size=bin_size,
            bins=bins,
            total_estimated_volume_usd=round(total_volume, 2),
            is_complete=True,
        )
