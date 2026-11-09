"""Ruta de API para obtención de velas japonesas OHLCV para TradingView."""

from __future__ import annotations

import time
from typing import Any
import aiohttp
from fastapi import APIRouter, Query, Response, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/klines", tags=["Klines & Candlesticks"])

SUPPORTED_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "4h", "1d"}
BINANCE_KLINES_URL = "https://fapi.binance.com/fapi/v1/klines"

# Caché en memoria para evitar saturación de peticiones (TTL 5s)
_klines_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}


@router.get(
    "/{symbol}",
    summary="Velas japonesas OHLCV de Binance Futures",
    description="Retorna velas con timestamps Unix en segundos para integración con TradingView Lightweight Charts.",
)
async def get_klines(
    symbol: str,
    interval: str = Query(default="1h", description="Intervalo temporal: 15m, 1h, 4h, 1d"),
    limit: int = Query(default=100, ge=10, le=500, description="Número de velas"),
) -> list[dict[str, Any]]:
    """Consulta las velas OHLCV de Binance con fallback sintético."""
    norm_sym = symbol.upper().strip()
    if interval not in SUPPORTED_INTERVALS:
        interval = "1h"

    cache_key = f"{norm_sym}_{interval}_{limit}"
    now = time.time()
    if cache_key in _klines_cache:
        ts, cached_data = _klines_cache[cache_key]
        if (now - ts) < 5.0:
            return cached_data

    url = f"{BINANCE_KLINES_URL}?symbol={norm_sym}&interval={interval}&limit={limit}"
    headers = {"User-Agent": "LiqScope/1.0"}

    try:
        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    raw_data = await resp.json()
                    candles: list[dict[str, Any]] = []
                    for row in raw_data:
                        # row: [open_time, open, high, low, close, volume, ...]
                        open_time_sec = int(row[0] // 1000)
                        o = float(row[1])
                        h = float(row[2])
                        l = float(row[3])
                        c = float(row[4])
                        v = float(row[5])
                        candles.append({
                            "time": open_time_sec,
                            "open": o,
                            "high": h,
                            "low": l,
                            "close": c,
                            "volume": v,
                        })
                    _klines_cache[cache_key] = (now, candles)
                    return candles
    except Exception:
        pass

    # Fallback sintético en caso de problemas de red o modo demo
    base_price = 74600.0 if norm_sym == "BTCUSDT" else 2120.0
    interval_seconds = 3600 if interval == "1h" else (900 if interval == "15m" else 14400)
    current_time_sec = int(time.time() // interval_seconds) * interval_seconds
    fallback_candles: list[dict[str, Any]] = []

    p = base_price * 0.98
    for i in range(limit):
        candle_time = current_time_sec - (limit - i) * interval_seconds
        change = ((i * 37) % 100 - 48) * (base_price * 0.001)
        c = max(p + change, 10.0)
        o = p
        h = max(o, c) + abs(change) * 0.5
        l = min(o, c) - abs(change) * 0.5
        v = 500.0 + (i % 20) * 50.0
        fallback_candles.append({
            "time": candle_time,
            "open": round(o, 2),
            "high": round(h, 2),
            "low": round(l, 2),
            "close": round(c, 2),
            "volume": round(v, 2),
        })
        p = c

    _klines_cache[cache_key] = (now, fallback_candles)
    return fallback_candles


BINANCE_OI_HIST_URL = "https://fapi.binance.com/futures/data/openInterestHist"
BINANCE_FUNDING_HIST_URL = "https://fapi.binance.com/fapi/v1/fundingRate"

_oi_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}
_funding_hist_cache: dict[str, tuple[float, list[dict[str, Any]]]] = {}


@router.get(
    "/{symbol}/open-interest",
    summary="Histórico de Open Interest para Súper Gráficos",
    description="Retorna el histórico de Open Interest (nocional USD y contratos) para sub-panel sincronizado en TradingView.",
)
async def get_open_interest_history(
    symbol: str,
    interval: str = Query(default="1h", description="Intervalo temporal: 15m, 1h, 4h, 1d"),
    limit: int = Query(default=100, ge=10, le=500, description="Número de puntos"),
) -> list[dict[str, Any]]:
    """Consulta el histórico de Open Interest en Binance Futures."""
    norm_sym = symbol.upper().strip()
    period = interval if interval in {"5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"} else "1h"
    cache_key = f"{norm_sym}_{period}_{limit}"
    now = time.time()
    if cache_key in _oi_cache:
        ts, cached_data = _oi_cache[cache_key]
        if (now - ts) < 8.0:
            return cached_data

    url = f"{BINANCE_OI_HIST_URL}?symbol={norm_sym}&period={period}&limit={limit}"
    headers = {"User-Agent": "LiqScope/1.0"}

    try:
        timeout = aiohttp.ClientTimeout(total=4.5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    raw_data = await resp.json()
                    oi_points: list[dict[str, Any]] = []
                    seen_times: set[int] = set()
                    for row in raw_data:
                        t = int(row["timestamp"] // 1000)
                        if t not in seen_times:
                            seen_times.add(t)
                            oi_points.append({
                                "time": t,
                                "value": round(float(row["sumOpenInterestValue"]), 2),
                                "coins": round(float(row["sumOpenInterest"]), 2),
                            })
                    oi_points.sort(key=lambda x: x["time"])
                    if oi_points:
                        _oi_cache[cache_key] = (now, oi_points)
                        return oi_points
    except Exception:
        pass

    # Fallback sintético elegante
    interval_seconds = 3600 if interval == "1h" else (900 if interval == "15m" else 14400)
    current_time_sec = int(time.time() // interval_seconds) * interval_seconds
    base_oi = 7200000000.0 if norm_sym == "BTCUSDT" else 2100000000.0
    fallback_oi: list[dict[str, Any]] = []
    for i in range(limit):
        t = current_time_sec - (limit - i) * interval_seconds
        factor = 1.0 + (((i * 17) % 50 - 25) * 0.002)
        val = base_oi * factor
        fallback_oi.append({
            "time": t,
            "value": round(val, 2),
            "coins": round(val / 75000.0, 2),
        })
    _oi_cache[cache_key] = (now, fallback_oi)
    return fallback_oi


@router.get(
    "/{symbol}/funding-history",
    summary="Histórico de Funding Rates para Súper Gráficos",
    description="Retorna el histórico de tasas de financiación para sub-panel sincronizado en TradingView.",
)
async def get_funding_history(
    symbol: str,
    limit: int = Query(default=100, ge=10, le=500, description="Número de liquidaciones de tasa"),
) -> list[dict[str, Any]]:
    """Consulta el histórico de liquidaciones de tasa de financiación en Binance Futures."""
    norm_sym = symbol.upper().strip()
    cache_key = f"{norm_sym}_{limit}"
    now = time.time()
    if cache_key in _funding_hist_cache:
        ts, cached_data = _funding_hist_cache[cache_key]
        if (now - ts) < 15.0:
            return cached_data

    url = f"{BINANCE_FUNDING_HIST_URL}?symbol={norm_sym}&limit={limit}"
    headers = {"User-Agent": "LiqScope/1.0"}

    try:
        timeout = aiohttp.ClientTimeout(total=4.5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    raw_data = await resp.json()
                    funding_points: list[dict[str, Any]] = []
                    seen_times: set[int] = set()
                    sorted_rows = sorted(raw_data, key=lambda x: x["fundingTime"])
                    for row in sorted_rows:
                        t = int(row["fundingTime"] // 1000)
                        rate_pct = float(row["fundingRate"]) * 100
                        if t not in seen_times:
                            seen_times.add(t)
                            funding_points.append({
                                "time": t,
                                "value": round(rate_pct, 4),
                                "color": "rgba(0, 240, 144, 0.85)" if rate_pct >= 0 else "rgba(255, 51, 88, 0.85)",
                            })
                    if funding_points:
                        _funding_hist_cache[cache_key] = (now, funding_points)
                        return funding_points
    except Exception:
        pass

    # Fallback sintético
    current_time_sec = int(time.time() // 28800) * 28800
    fallback_f: list[dict[str, Any]] = []
    for i in range(limit):
        t = current_time_sec - (limit - i) * 28800
        rate = 0.01 + (((i * 29) % 30 - 12) * 0.001)
        fallback_f.append({
            "time": t,
            "value": round(rate, 4),
            "color": "rgba(0, 240, 144, 0.85)" if rate >= 0 else "rgba(255, 51, 88, 0.85)",
        })
    _funding_hist_cache[cache_key] = (now, fallback_f)
    return fallback_f
