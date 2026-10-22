"""Escalones oficiales de Margen de Mantenimiento (MMR) para Binance Futures USDⓈ-M.

Alcance: Fase 2 limitada a Binance USDⓈ-M (BTCUSDT y ETHUSDT).
Fuente Oficial: https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin
Fecha de Consulta: 2026-10-22
"""

from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class MarginTier:
    """Representa un escalón de riesgo y margen de mantenimiento oficial."""

    tier: int
    min_notional: float
    max_notional: float
    maintenance_margin_rate: float  # MMR expresado en decimal (ej. 0.004 = 0.4%)
    cum_maintenance_amount: float  # Deducción acumulada de margen
    max_leverage: int
    status: str  # 'VERIFIED' o 'PENDING_VERIFICATION'
    official_url: str
    consulted_at: str


OFFICIAL_TIERS_URL: Final[str] = (
    "https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin"
)
CONSULTATION_DATE: Final[str] = "2026-10-22"

# Tiers verificados para BTCUSDT (Binance Futures USDⓈ-M)
BINANCE_BTCUSDT_TIERS: Final[list[MarginTier]] = [
    MarginTier(
        tier=1,
        min_notional=0.0,
        max_notional=50_000.0,
        maintenance_margin_rate=0.004,  # 0.40%
        cum_maintenance_amount=0.0,
        max_leverage=125,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=2,
        min_notional=50_000.0,
        max_notional=250_000.0,
        maintenance_margin_rate=0.005,  # 0.50%
        cum_maintenance_amount=50.0,
        max_leverage=100,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=3,
        min_notional=250_000.0,
        max_notional=1_000_000.0,
        maintenance_margin_rate=0.010,  # 1.00%
        cum_maintenance_amount=1_300.0,
        max_leverage=50,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=4,
        min_notional=1_000_000.0,
        max_notional=5_000_000.0,
        maintenance_margin_rate=0.025,  # 2.50%
        cum_maintenance_amount=16_300.0,
        max_leverage=20,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=5,
        min_notional=5_000_000.0,
        max_notional=float("inf"),
        maintenance_margin_rate=0.050,  # 5.00% estimado para tramos institucionales
        cum_maintenance_amount=141_300.0,
        max_leverage=10,
        status="PENDING_VERIFICATION",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
]

# Tiers verificados para ETHUSDT (Binance Futures USDⓈ-M)
BINANCE_ETHUSDT_TIERS: Final[list[MarginTier]] = [
    MarginTier(
        tier=1,
        min_notional=0.0,
        max_notional=25_000.0,
        maintenance_margin_rate=0.005,  # 0.50%
        cum_maintenance_amount=0.0,
        max_leverage=100,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=2,
        min_notional=25_000.0,
        max_notional=150_000.0,
        maintenance_margin_rate=0.010,  # 1.00%
        cum_maintenance_amount=125.0,
        max_leverage=50,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=3,
        min_notional=150_000.0,
        max_notional=500_000.0,
        maintenance_margin_rate=0.020,  # 2.00%
        cum_maintenance_amount=1_625.0,
        max_leverage=25,
        status="VERIFIED",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
    MarginTier(
        tier=4,
        min_notional=500_000.0,
        max_notional=float("inf"),
        maintenance_margin_rate=0.050,  # 5.00%
        cum_maintenance_amount=16_625.0,
        max_leverage=10,
        status="PENDING_VERIFICATION",
        official_url=OFFICIAL_TIERS_URL,
        consulted_at=CONSULTATION_DATE,
    ),
]


def get_tier_for_notional(symbol: str, notional_usd: float) -> MarginTier:
    """Retorna el escalón de margen correspondiente según el símbolo y nocional en USD."""
    sym = symbol.upper()
    if sym == "BTCUSDT":
        tiers = BINANCE_BTCUSDT_TIERS
    elif sym == "ETHUSDT":
        tiers = BINANCE_ETHUSDT_TIERS
    else:
        # Fallback genérico para otros símbolos aún no verificados
        return MarginTier(
            tier=1,
            min_notional=0.0,
            max_notional=float("inf"),
            maintenance_margin_rate=0.005,
            cum_maintenance_amount=0.0,
            max_leverage=20,
            status="PENDING_VERIFICATION",
            official_url=OFFICIAL_TIERS_URL,
            consulted_at=CONSULTATION_DATE,
        )

    for tier in tiers:
        if tier.min_notional <= notional_usd < tier.max_notional:
            return tier

    # Retornar el último escalón por defecto
    return tiers[-1]
