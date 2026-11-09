"""Modelos Pydantic para el Screener de Mercado: Ganadoras, Perdedoras y OI Surge (Ballenas)."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class ScreenerItem(BaseModel):
    """Métrica individual de un activo de derivados para el Screener."""

    symbol: str = Field(description="Símbolo del par (ej. BTCUSDT)")
    base_coin: str = Field(description="Moneda base (ej. BTC)")
    price: float = Field(description="Precio actual de mercado")
    change_24h_pct: float = Field(description="Cambio porcentual en 24h")
    high_24h: float = Field(description="Precio máximo en 24h")
    low_24h: float = Field(description="Precio mínimo en 24h")
    volume_24h_usd: float = Field(description="Volumen nocional en 24h (USD)")
    open_interest_usd: float = Field(description="Interés Abierto total actual (USD)")
    oi_change_pct: float = Field(default=0.0, description="Variación porcentual de OI reciente")
    oi_to_vol_ratio: float = Field(default=0.0, description="Ratio Open Interest / Volumen 24h")
    funding_rate: float = Field(default=0.01, description="Tasa de financiación actual (8h)")
    whale_signal: Literal["ACCUMULATION", "DISTRIBUTION", "SQUEEZE_RISK", "NORMAL"] = Field(
        default="NORMAL",
        description="Señal algorítmica de detección de ballenas e interés institucional",
    )
    is_whale_alert: bool = Field(default=False, description="Indica si hay un pico inusual de ballenas")


class MarketBreadth(BaseModel):
    """Amplitud de mercado y barómetro global de derivados."""

    total_tracked: int = Field(description="Número de pares analizados con liquidez activa")
    advancers: int = Field(description="Pares en verde (alcistas)")
    decliners: int = Field(description="Pares en rojo (bajistas)")
    advancers_pct: float = Field(description="Porcentaje de pares alcistas")
    decliners_pct: float = Field(description="Porcentaje de pares bajistas")
    market_sentiment: Literal["BULLISH_EXPANSION", "BEARISH_CONTRACTION", "NEUTRAL"] = Field(
        description="Sesgo macro de amplitud de derivados",
    )
    total_market_oi_usd: float = Field(description="Open Interest global agregado (USD)")
    total_market_vol_usd: float = Field(description="Volumen global agregado 24h (USD)")


class ScreenerResponse(BaseModel):
    """Respuesta completa del Screener de Mercado."""

    breadth: MarketBreadth
    top_gainers: list[ScreenerItem]
    top_losers: list[ScreenerItem]
    oi_surge: list[ScreenerItem]
    all_items: list[ScreenerItem]
    timestamp: int = Field(description="Unix timestamp de actualización")
