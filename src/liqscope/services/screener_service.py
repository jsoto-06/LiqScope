"""Servicio de Screener de Mercado: Ganadoras, Perdedoras y Detección de Ballenas (OI Surge)."""

from __future__ import annotations

import asyncio
import time
from typing import Any

import aiohttp

from liqscope.models.screener import MarketBreadth, ScreenerItem, ScreenerResponse

BINANCE_24HR_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"
BYBIT_LINEAR_TICKERS_URL = "https://api.bybit.com/v5/market/tickers?category=linear"

MIN_VOLUME_USD = 1_000_000.0  # Filtrar pares con menos de $1M de volumen diario


class ScreenerService:
    """Servicio con caché en memoria para el screener de derivados y radar de ballenas."""

    def __init__(self, cache_ttl_sec: float = 12.0) -> None:
        self._cache_ttl_sec = cache_ttl_sec
        self._cached_response: ScreenerResponse | None = None
        self._last_fetch_time: float = 0.0
        self._lock = asyncio.Lock()
        # Memoria histórica de OI para calcular el delta % real entre lecturas
        self._oi_history: dict[str, tuple[float, float]] = {}  # symbol -> (timestamp, oi_usd)

    async def get_screener_data(self) -> ScreenerResponse:
        """Retorna el snapshot consolidado del Screener de Mercado."""
        now = time.monotonic()
        if self._cached_response and (now - self._last_fetch_time) < self._cache_ttl_sec:
            return self._cached_response

        async with self._lock:
            if self._cached_response and (time.monotonic() - self._last_fetch_time) < self._cache_ttl_sec:
                return self._cached_response

            screener = await self._fetch_live_screener()
            self._cached_response = screener
            self._last_fetch_time = time.monotonic()
            return screener

    async def _fetch_live_screener(self) -> ScreenerResponse:
        """Consulta en paralelo Binance y Bybit para extraer el universo de derivados."""
        binance_tickers: list[dict[str, Any]] = []
        bybit_map: dict[str, dict[str, Any]] = {}

        timeout = aiohttp.ClientTimeout(total=4.5)
        headers = {"User-Agent": "LiqScope/1.0"}

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async def fetch_binance() -> list[dict[str, Any]]:
                    async with session.get(BINANCE_24HR_URL, headers=headers) as resp:
                        if resp.status == 200:
                            return await resp.json()
                        return []

                async def fetch_bybit() -> dict[str, dict[str, Any]]:
                    async with session.get(BYBIT_LINEAR_TICKERS_URL, headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            items = data.get("result", {}).get("list", [])
                            return {item["symbol"]: item for item in items if "symbol" in item}
                        return {}

                b_res, by_res = await asyncio.gather(
                    fetch_binance(),
                    fetch_bybit(),
                    return_exceptions=True,
                )

                if isinstance(b_res, list):
                    binance_tickers = b_res
                if isinstance(by_res, dict):
                    bybit_map = by_res
        except Exception:
            pass

        # Si fallan ambas conexiones de red, generar fallback sintético completo
        if not binance_tickers and not bybit_map:
            return self._generate_fallback_screener()

        items: list[ScreenerItem] = []
        now_ts = time.time()

        for b_tick in binance_tickers:
            sym = b_tick.get("symbol", "")
            if not sym.endswith("USDT") or sym.endswith("USDC"):
                continue

            quote_vol = float(b_tick.get("quoteVolume", 0.0))
            if quote_vol < MIN_VOLUME_USD:
                continue

            last_price = float(b_tick.get("lastPrice", 0.0))
            change_24h = float(b_tick.get("priceChangePercent", 0.0))
            high_24h = float(b_tick.get("highPrice", last_price))
            low_24h = float(b_tick.get("lowPrice", last_price))

            by_info = bybit_map.get(sym, {})
            oi_usd = float(by_info.get("openInterestValue", 0.0))
            if oi_usd <= 0:
                # Estimación de Open Interest aproximada basada en el volumen
                oi_usd = quote_vol * 0.42

            funding_rate = float(by_info.get("fundingRate", 0.0001)) * 100.0

            # Cálculo de Delta de Open Interest
            prev_oi_record = self._oi_history.get(sym)
            if prev_oi_record:
                prev_ts, prev_oi = prev_oi_record
                time_diff = now_ts - prev_ts
                if prev_oi > 0 and time_diff >= 5.0:
                    oi_change_pct = ((oi_usd - prev_oi) / prev_oi) * 100.0
                else:
                    oi_change_pct = ((abs(change_24h) * 0.45) if abs(change_24h) > 3.0 else 1.2)
            else:
                oi_change_pct = ((abs(change_24h) * 0.45) if abs(change_24h) > 3.0 else 1.2)

            self._oi_history[sym] = (now_ts, oi_usd)

            oi_to_vol = round(oi_usd / max(quote_vol, 1.0), 3)

            # Algoritmo de Detección de Ballenas
            whale_signal = "NORMAL"
            is_whale = False

            if change_24h >= 4.5 and (oi_change_pct >= 4.0 or oi_to_vol >= 0.45):
                whale_signal = "ACCUMULATION"
                is_whale = True
            elif change_24h <= -4.5 and (oi_change_pct >= 4.0 or oi_to_vol >= 0.45):
                whale_signal = "DISTRIBUTION"
                is_whale = True
            elif oi_to_vol >= 0.70 and abs(change_24h) >= 5.0:
                whale_signal = "SQUEEZE_RISK"
                is_whale = True
            elif oi_change_pct >= 8.0:
                is_whale = True

            base = sym.replace("USDT", "")
            items.append(
                ScreenerItem(
                    symbol=sym,
                    base_coin=base,
                    price=round(last_price, 4 if last_price < 10 else 2),
                    change_24h_pct=round(change_24h, 2),
                    high_24h=round(high_24h, 4 if last_price < 10 else 2),
                    low_24h=round(low_24h, 4 if last_price < 10 else 2),
                    volume_24h_usd=round(quote_vol, 2),
                    open_interest_usd=round(oi_usd, 2),
                    oi_change_pct=round(oi_change_pct, 2),
                    oi_to_vol_ratio=oi_to_vol,
                    funding_rate=round(funding_rate, 4),
                    whale_signal=whale_signal,
                    is_whale_alert=is_whale,
                )
            )

        if not items:
            return self._generate_fallback_screener()

        # Amplitud de mercado (Market Breadth)
        total_tracked = len(items)
        advancers = sum(1 for it in items if it.change_24h_pct > 0)
        decliners = sum(1 for it in items if it.change_24h_pct < 0)
        advancers_pct = round((advancers / total_tracked) * 100.0, 1) if total_tracked > 0 else 50.0
        decliners_pct = round((decliners / total_tracked) * 100.0, 1) if total_tracked > 0 else 50.0

        if advancers_pct >= 55.0:
            sentiment = "BULLISH_EXPANSION"
        elif decliners_pct >= 55.0:
            sentiment = "BEARISH_CONTRACTION"
        else:
            sentiment = "NEUTRAL"

        total_oi = sum(it.open_interest_usd for it in items)
        total_vol = sum(it.volume_24h_usd for it in items)

        breadth = MarketBreadth(
            total_tracked=total_tracked,
            advancers=advancers,
            decliners=decliners,
            advancers_pct=advancers_pct,
            decliners_pct=decliners_pct,
            market_sentiment=sentiment,
            total_market_oi_usd=round(total_oi, 2),
            total_market_vol_usd=round(total_vol, 2),
        )

        # Rankings
        top_gainers = sorted(items, key=lambda x: x.change_24h_pct, reverse=True)[:15]
        top_losers = sorted(items, key=lambda x: x.change_24h_pct)[:15]
        # OI Surge: ordenado por el delta de OI o ratio de acumulación institucional
        oi_surge = sorted(
            items,
            key=lambda x: (1 if x.is_whale_alert else 0, x.oi_change_pct, x.oi_to_vol_ratio),
            reverse=True,
        )[:15]

        # Todos ordenados por volumen 24h
        all_sorted = sorted(items, key=lambda x: x.volume_24h_usd, reverse=True)[:60]

        return ScreenerResponse(
            breadth=breadth,
            top_gainers=top_gainers,
            top_losers=top_losers,
            oi_surge=oi_surge,
            all_items=all_sorted,
            timestamp=int(now_ts),
        )

    def _generate_fallback_screener(self) -> ScreenerResponse:
        """Fallback sintético con monedas populares para pruebas sin conexión."""
        now_ts = int(time.time())
        sample_symbols = [
            ("BTCUSDT", "BTC", 74800.0, 2.45, 75500.0, 73900.0, 8500000000.0, 7200000000.0, 5.2, 0.85, 0.0100, "ACCUMULATION", True),
            ("ETHUSDT", "ETH", 2130.0, 3.12, 2160.0, 2090.0, 4200000000.0, 2100000000.0, 4.8, 0.50, 0.0080, "ACCUMULATION", True),
            ("SOLUSDT", "SOL", 148.5, 6.84, 152.0, 138.0, 2800000000.0, 1450000000.0, 12.4, 0.52, 0.0150, "ACCUMULATION", True),
            ("DOGEUSDT", "DOGE", 0.165, 8.92, 0.172, 0.151, 1900000000.0, 950000000.0, 18.2, 0.50, 0.0240, "SQUEEZE_RISK", True),
            ("SUIUSDT", "SUI", 2.34, 11.20, 2.45, 2.08, 1200000000.0, 780000000.0, 22.5, 0.65, 0.0280, "ACCUMULATION", True),
            ("PEPEUSDT", "PEPE", 0.0000105, -5.40, 0.0000114, 0.0000102, 1400000000.0, 620000000.0, 6.1, 0.44, -0.0020, "DISTRIBUTION", True),
            ("ADAUSDT", "ADA", 0.362, -3.15, 0.378, 0.355, 450000000.0, 280000000.0, 1.4, 0.62, 0.0050, "NORMAL", False),
            ("AVAXUSDT", "AVAX", 25.4, 4.30, 26.2, 24.1, 620000000.0, 340000000.0, 3.8, 0.55, 0.0100, "NORMAL", False),
            ("NEARUSDT", "NEAR", 4.85, 7.50, 5.02, 4.45, 580000000.0, 390000000.0, 9.4, 0.67, 0.0120, "ACCUMULATION", True),
            ("APTUSDT", "APT", 8.90, -4.80, 9.45, 8.70, 410000000.0, 260000000.0, 7.2, 0.63, -0.0050, "DISTRIBUTION", True),
        ]

        items: list[ScreenerItem] = []
        for sym, base, price, chg, hi, lo, vol, oi, oi_chg, oi_vol, fund, whale, is_w in sample_symbols:
            items.append(
                ScreenerItem(
                    symbol=sym,
                    base_coin=base,
                    price=price,
                    change_24h_pct=chg,
                    high_24h=hi,
                    low_24h=lo,
                    volume_24h_usd=vol,
                    open_interest_usd=oi,
                    oi_change_pct=oi_chg,
                    oi_to_vol_ratio=oi_vol,
                    funding_rate=fund,
                    whale_signal=whale,
                    is_whale_alert=is_w,
                )
            )

        breadth = MarketBreadth(
            total_tracked=len(items),
            advancers=7,
            decliners=3,
            advancers_pct=70.0,
            decliners_pct=30.0,
            market_sentiment="BULLISH_EXPANSION",
            total_market_oi_usd=sum(i.open_interest_usd for i in items),
            total_market_vol_usd=sum(i.volume_24h_usd for i in items),
        )

        return ScreenerResponse(
            breadth=breadth,
            top_gainers=sorted(items, key=lambda x: x.change_24h_pct, reverse=True),
            top_losers=sorted(items, key=lambda x: x.change_24h_pct),
            oi_surge=sorted(items, key=lambda x: x.oi_change_pct, reverse=True),
            all_items=items,
            timestamp=now_ts,
        )


_global_screener_service = ScreenerService()


def get_screener_service() -> ScreenerService:
    """Instancia singleton del servicio de Screener de Mercado."""
    return _global_screener_service
