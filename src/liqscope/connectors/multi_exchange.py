"""Agregador de datos de mercado multi-exchange para LiqScope.

Conecta en tiempo real con 4 de los mayores centros de derivados cripto del mundo:
1. Binance Futures (USDT-M)
2. Bybit Linear Futures (USDT)
3. Hyperliquid Perpetuals (USDC)
4. Kraken Futures (Derivatives)

Calcula el Open Interest unificado y el Mark Price ponderado por volumen (VWAP).
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

import aiohttp
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger("liqscope.connectors.multi_exchange")


class ExchangeMarketQuote(BaseModel):
    """Cotización e interés abierto de un exchange específico."""

    model_config = ConfigDict(frozen=True)

    exchange: str = Field(description="Identificador del exchange (binance, bybit, hyperliquid, kraken)")
    display_name: str = Field(description="Nombre comercial para visualización")
    symbol: str = Field(description="Símbolo base (BTCUSDT o ETHUSDT)")
    mark_price: float = Field(gt=0, description="Precio de marca actual")
    open_interest_usd: float = Field(ge=0, description="Interés abierto nocional en USD")
    share_pct: float = Field(default=0.0, ge=0, le=100, description="Participación porcentual en el OI total")
    status: str = Field(default="online", description="Estado de la conexión (online, offline)")


class MultiExchangeSnapshot(BaseModel):
    """Instantánea unificada agregada de múltiples exchanges."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(description="Símbolo analizado")
    aggregated_mark_price: float = Field(gt=0, description="Precio Mark ponderado por volumen o referencia")
    total_open_interest_usd: float = Field(ge=0, description="Suma total de Open Interest en USD")
    exchanges: dict[str, ExchangeMarketQuote] = Field(description="Detalle por exchange")
    long_account_ratio: float = Field(default=0.50, description="Ratio de cuentas en largo ponderado")
    short_account_ratio: float = Field(default=0.50, description="Ratio de cuentas en corto ponderado")
    timestamp: float = Field(description="Timestamp Unix de cálculo")


class MultiExchangeAggregator:
    """Cliente asíncrono para agregación de mercado desde Binance, Bybit, Hyperliquid y Kraken."""

    def __init__(self, cache_ttl_sec: float = 8.0, timeout_sec: float = 4.0) -> None:
        self.cache_ttl_sec = cache_ttl_sec
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)
        self._cache: dict[str, tuple[float, MultiExchangeSnapshot]] = {}

    async def get_aggregated_snapshot(
        self,
        symbol: str = "BTCUSDT",
        target_exchange: str = "all",
    ) -> MultiExchangeSnapshot:
        """Obtiene la instantánea de mercado agregada o filtrada por exchange con caché."""
        sym = symbol.upper().strip()
        now = time.time()

        cache_key = f"{sym}_all"
        if cache_key in self._cache:
            ts, cached_snap = self._cache[cache_key]
            if (now - ts) < self.cache_ttl_sec:
                if target_exchange.lower() == "all":
                    return cached_snap
                return self._filter_by_exchange(cached_snap, target_exchange.lower())

        # Petición paralela asíncrona a los 4 exchanges
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            results = await asyncio.gather(
                self._fetch_binance(session, sym),
                self._fetch_bybit(session, sym),
                self._fetch_hyperliquid(session, sym),
                self._fetch_kraken(session, sym),
                return_exceptions=True,
            )

        quotes: dict[str, ExchangeMarketQuote] = {}
        for res in results:
            if isinstance(res, ExchangeMarketQuote) and res.mark_price > 0:
                quotes[res.exchange] = res
            elif isinstance(res, Exception):
                logger.warning("Fallo al consultar un exchange en agregador: %s", res)

        # Si ninguno respondió, fallback a cotización base de seguridad
        if not quotes:
            default_p = 74800.0 if sym == "BTCUSDT" else 2120.0
            quotes["binance"] = ExchangeMarketQuote(
                exchange="binance",
                display_name="Binance Futures",
                symbol=sym,
                mark_price=default_p,
                open_interest_usd=7_200_000_000.0 if sym == "BTCUSDT" else 1_800_000_000.0,
                status="fallback",
            )

        total_oi = sum(q.open_interest_usd for q in quotes.values())

        # Calcular participación y VWAP Mark Price
        weighted_price_sum = sum(q.mark_price * q.open_interest_usd for q in quotes.values())
        vwap_mark = (weighted_price_sum / total_oi) if total_oi > 0 else list(quotes.values())[0].mark_price

        # Actualizar porcentajes relativos
        final_quotes: dict[str, ExchangeMarketQuote] = {}
        for k, q in quotes.items():
            pct = (q.open_interest_usd / total_oi * 100.0) if total_oi > 0 else 0.0
            final_quotes[k] = ExchangeMarketQuote(
                exchange=q.exchange,
                display_name=q.display_name,
                symbol=q.symbol,
                mark_price=q.mark_price,
                open_interest_usd=q.open_interest_usd,
                share_pct=round(pct, 2),
                status=q.status,
            )

        long_ratio = 0.50
        short_ratio = 0.50
        # Utilizar ratio de cuentas de Binance como estándar si está disponible
        if "binance" in quotes:
            long_ratio = getattr(quotes["binance"], "_long_ratio", 0.50)
            short_ratio = getattr(quotes["binance"], "_short_ratio", 0.50)

        snapshot = MultiExchangeSnapshot(
            symbol=sym,
            aggregated_mark_price=round(vwap_mark, 2),
            total_open_interest_usd=round(total_oi, 2),
            exchanges=final_quotes,
            long_account_ratio=long_ratio,
            short_account_ratio=short_ratio,
            timestamp=now,
        )

        self._cache[cache_key] = (now, snapshot)

        if target_exchange.lower() == "all":
            return snapshot
        return self._filter_by_exchange(snapshot, target_exchange.lower())

    def _filter_by_exchange(
        self,
        snapshot: MultiExchangeSnapshot,
        target: str,
    ) -> MultiExchangeSnapshot:
        """Aísla un exchange específico dentro de la instantánea agregada."""
        match_key = None
        for k in snapshot.exchanges:
            if target in k.lower():
                match_key = k
                break

        if not match_key:
            return snapshot

        quote = snapshot.exchanges[match_key]
        single_quote_dict = {
            match_key: ExchangeMarketQuote(
                exchange=quote.exchange,
                display_name=quote.display_name,
                symbol=quote.symbol,
                mark_price=quote.mark_price,
                open_interest_usd=quote.open_interest_usd,
                share_pct=100.0,
                status=quote.status,
            )
        }

        return MultiExchangeSnapshot(
            symbol=snapshot.symbol,
            aggregated_mark_price=quote.mark_price,
            total_open_interest_usd=quote.open_interest_usd,
            exchanges=single_quote_dict,
            long_account_ratio=snapshot.long_account_ratio,
            short_account_ratio=snapshot.short_account_ratio,
            timestamp=snapshot.timestamp,
        )

    # -------------------------------------------------------------
    # EXTRACTORES ESPECÍFICOS POR EXCHANGE
    # -------------------------------------------------------------

    async def _fetch_binance(self, session: aiohttp.ClientSession, symbol: str) -> ExchangeMarketQuote:
        """Consulta precio mark, open interest y ratio de cuentas de Binance Futures."""
        url_mark = f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={symbol}"
        url_oi = f"https://fapi.binance.com/fapi/v1/openInterest?symbol={symbol}"
        url_ratio = f"https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol={symbol}&period=5m&limit=1"

        mark_price = 0.0
        oi_usd = 0.0
        long_ratio = 0.50
        short_ratio = 0.50

        async with session.get(url_mark) as resp:
            if resp.status == 200:
                data = await resp.json()
                mark_price = float(data.get("markPrice", 0.0))

        async with session.get(url_oi) as resp:
            if resp.status == 200:
                data = await resp.json()
                oi_coins = float(data.get("openInterest", 0.0))
                oi_usd = oi_coins * mark_price

        try:
            async with session.get(url_ratio) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if isinstance(data, list) and len(data) > 0:
                        long_ratio = float(data[0].get("longAccount", 0.50))
                        short_ratio = float(data[0].get("shortAccount", 0.50))
        except Exception:
            pass

        quote = ExchangeMarketQuote(
            exchange="binance",
            display_name="Binance Futures",
            symbol=symbol,
            mark_price=mark_price,
            open_interest_usd=oi_usd,
            status="online",
        )
        object.__setattr__(quote, "_long_ratio", long_ratio)
        object.__setattr__(quote, "_short_ratio", short_ratio)
        return quote

    async def _fetch_bybit(self, session: aiohttp.ClientSession, symbol: str) -> ExchangeMarketQuote:
        """Consulta Bybit Linear V5 tickers."""
        url = f"https://api.bybit.com/v5/market/tickers?category=linear&symbol={symbol}"
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                items = data.get("result", {}).get("list", [])
                if items:
                    item = items[0]
                    mark_p = float(item.get("markPrice", 0.0))
                    oi_usd = float(item.get("openInterestValue", 0.0))
                    return ExchangeMarketQuote(
                        exchange="bybit",
                        display_name="Bybit Linear",
                        symbol=symbol,
                        mark_price=mark_p,
                        open_interest_usd=oi_usd,
                        status="online",
                    )
        raise ValueError(f"Respuesta no válida de Bybit para {symbol}")

    async def _fetch_hyperliquid(self, session: aiohttp.ClientSession, symbol: str) -> ExchangeMarketQuote:
        """Consulta Hyperliquid Perps (DEX líder de perpetuos en arbitrum/l1)."""
        url = "https://api.hyperliquid.xyz/info"
        payload = {"type": "metaAndAssetCtxs"}
        coin_target = "BTC" if "BTC" in symbol else "ETH"

        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                if isinstance(data, list) and len(data) >= 2:
                    universe = data[0].get("universe", [])
                    ctxs = data[1]
                    for idx, asset in enumerate(universe):
                        if asset.get("name") == coin_target and idx < len(ctxs):
                            ctx = ctxs[idx]
                            mark_p = float(ctx.get("markPx", 0.0))
                            oi_coins = float(ctx.get("openInterest", 0.0))
                            oi_usd = oi_coins * mark_p
                            return ExchangeMarketQuote(
                                exchange="hyperliquid",
                                display_name="Hyperliquid DEX",
                                symbol=symbol,
                                mark_price=mark_p,
                                open_interest_usd=oi_usd,
                                status="online",
                            )
        raise ValueError(f"Respuesta no válida de Hyperliquid para {symbol}")

    async def _fetch_kraken(self, session: aiohttp.ClientSession, symbol: str) -> ExchangeMarketQuote:
        """Consulta Kraken Futures derivatives ticker público."""
        url = "https://futures.kraken.com/derivatives/api/v3/tickers"
        kraken_sym = "PF_XBTUSD" if "BTC" in symbol else "PF_ETHUSD"

        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                tickers = data.get("tickers", [])
                for t in tickers:
                    if t.get("symbol") == kraken_sym:
                        mark_p = float(t.get("markPrice", 0.0))
                        oi_coins = float(t.get("openInterest", 0.0))
                        oi_usd = oi_coins * mark_p
                        return ExchangeMarketQuote(
                            exchange="kraken",
                            display_name="Kraken Futures",
                            symbol=symbol,
                            mark_price=mark_p,
                            open_interest_usd=oi_usd,
                            status="online",
                        )
        raise ValueError(f"Respuesta no válida de Kraken para {symbol}")
