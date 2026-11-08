"""Cliente REST asíncrono para Binance Futures USDⓈ-M (Fase 4).

Endpoints utilizados (Solo lectura pública):
- GET /fapi/v1/openInterest?symbol={symbol}
- GET /fapi/v1/premiumIndex?symbol={symbol}

Alcance estricto: Únicamente BTCUSDT y ETHUSDT.
Gestión de errores: HTTP 429/418 (Rate Limit) y respuestas unificadas con campo source.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Any, Self

import aiohttp
from pydantic import BaseModel, ConfigDict, Field

SUPPORTED_SYMBOLS: frozenset[str] = frozenset({"BTCUSDT", "ETHUSDT"})


class BinanceMarketData(BaseModel):
    """Datos de mercado en vivo extraídos de Binance Futures."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(description="Símbolo del contrato (BTCUSDT o ETHUSDT)")
    mark_price: float = Field(gt=0, description="Precio de marca actual (USD)")
    open_interest: float = Field(ge=0, description="Interés abierto en contratos/moneda base")
    open_interest_time: int = Field(description="Timestamp Unix en ms devuelto por openInterest")
    premium_index_time: int = Field(description="Timestamp Unix en ms devuelto por premiumIndex")
    source: str = Field(default="live", description="Origen de los datos ('live' o 'demo')")
    cached: bool = Field(default=False, description="Indica si proviene de la caché en memoria")
    data_age_sec: float = Field(
        default=0.0, ge=0, description="Antigüedad en segundos de los datos"
    )
    long_account_ratio: float = Field(
        default=0.50, ge=0.0, le=1.0, description="Ratio de cuentas en largo según Binance"
    )
    short_account_ratio: float = Field(
        default=0.50, ge=0.0, le=1.0, description="Ratio de cuentas en corto según Binance"
    )


class BinanceRestError(Exception):
    """Excepción base para errores de la API REST de Binance."""

    def __init__(
        self,
        message: str,
        code: str = "BINANCE_ERROR",
        status_code: int | None = None,
        source: str = "live",
        symbol: str | None = None,
        details: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.source = source
        self.symbol = symbol
        self.details = details

    def to_dict(self) -> dict[str, Any]:
        """Estructura normalizada de error con esquema contratado."""
        err_body: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "source": self.source,
        }
        if self.symbol is not None:
            err_body["symbol"] = self.symbol
        if self.details is not None:
            err_body["details"] = self.details
        return {"error": err_body}


class BinanceRateLimitError(BinanceRestError):
    """Excepción específica cuando se supera el límite de tasa de Binance (HTTP 429 o 418)."""

    def __init__(
        self,
        message: str = "Límite de peticiones de Binance alcanzado",
        code: str = "BINANCE_RATE_LIMIT_EXCEEDED",
        status_code: int = 429,
        retry_after: int | None = None,
        source: str = "live",
        symbol: str | None = None,
        details: str | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            source=source,
            symbol=symbol,
            details=details,
        )
        self.retry_after = retry_after

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        if self.retry_after is not None:
            data["error"]["retry_after"] = self.retry_after
        return data


class UnsupportedSymbolError(BinanceRestError):
    """Excepción lanzada cuando se solicita un par fuera del alcance de la Fase 4."""

    def __init__(
        self,
        symbol: str,
        code: str = "UNSUPPORTED_SYMBOL",
        status_code: int = 400,
        source: str = "live",
    ) -> None:
        message = (
            f"Símbolo no soportado en esta fase: '{symbol}'. "
            f"Solo se admiten: {', '.join(sorted(SUPPORTED_SYMBOLS))}."
        )
        super().__init__(
            message=message,
            code=code,
            status_code=status_code,
            source=source,
            symbol=symbol,
            details=f"Supported symbols: {sorted(SUPPORTED_SYMBOLS)}",
        )


class BinanceFuturesRestClient:
    """Cliente HTTP asíncrono para consultar Open Interest y Mark Price en Binance Futures."""

    _market_data_cache: dict[str, tuple[BinanceMarketData, float]] = {}
    _ratio_cache: dict[str, tuple[float, float, int, float]] = {}
    _fetch_locks: dict[str, asyncio.Lock] = {}

    @classmethod
    def _get_fetch_lock(cls, symbol: str) -> asyncio.Lock:
        if symbol not in cls._fetch_locks:
            cls._fetch_locks[symbol] = asyncio.Lock()
        return cls._fetch_locks[symbol]

    def __init__(
        self,
        base_url: str = "https://fapi.binance.com",
        session: aiohttp.ClientSession | None = None,
        timeout_sec: float = 5.0,
        cache_ttl_sec: float = 10.0,
        clock: Callable[[], float] = time.time,
    ) -> None:
        if timeout_sec <= 0:
            raise ValueError(
                f"timeout_sec debe ser estrictamente positivo (>0), recibido: {timeout_sec}"
            )
        self.base_url = base_url.rstrip("/")
        self._session = session
        self._owns_session = session is None
        self.timeout_sec = timeout_sec
        self.cache_ttl_sec = cache_ttl_sec
        self.clock = clock
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)

    @classmethod
    def clear_cache(cls) -> None:
        """Limpia la caché en memoria de datos de mercado, ratios y reinicia bloqueos."""
        cls._market_data_cache.clear()
        cls._ratio_cache.clear()
        cls._fetch_locks.clear()

    async def __aenter__(self) -> Self:
        await self._ensure_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        await self.close()

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self._owns_session = True
        return self._session

    async def close(self) -> None:
        """Cierra la sesión HTTP si fue creada internamente."""
        if self._owns_session and self._session is not None and not self._session.closed:
            await self._session.close()

    def validate_symbol(self, symbol: str) -> str:
        """Valida que el símbolo pertenezca estrictamente al conjunto admitido."""
        normalized = symbol.upper().strip()
        if normalized not in SUPPORTED_SYMBOLS:
            raise UnsupportedSymbolError(symbol=symbol)
        return normalized

    async def _request(
        self,
        path: str,
        params: dict[str, str],
        expected_type: type | tuple[type, ...] = dict,
    ) -> Any:
        """Ejecuta una petición GET y gestiona códigos de respuesta de Binance."""
        session = await self._ensure_session()
        url = f"{self.base_url}{path}"
        sym = params.get("symbol")

        try:
            async with session.get(url, params=params) as resp:
                status = resp.status
                if status == 200:
                    data = await resp.json()
                    if not isinstance(data, expected_type):
                        type_str = (
                            "dict"
                            if expected_type is dict
                            else ("list" if expected_type is list else str(expected_type))
                        )
                        raise BinanceRestError(
                            message=f"Respuesta inesperada de Binance (no {type_str}): {data}",
                            code="BINANCE_MALFORMED_RESPONSE",
                            status_code=status,
                            symbol=sym,
                            details=f"Formato no reconocido: {data}",
                        )
                    return data

                # Detección de Rate Limits HTTP 429 / 418
                if status in (429, 418):
                    retry_header = resp.headers.get("Retry-After")
                    retry_after = (
                        int(retry_header) if retry_header and retry_header.isdigit() else None
                    )
                    text = await resp.text()
                    code = "BINANCE_RATE_LIMIT_EXCEEDED" if status == 429 else "BINANCE_IP_BANNED"
                    raise BinanceRateLimitError(
                        message=f"Límite de peticiones de Binance alcanzado (HTTP {status})",
                        code=code,
                        status_code=status,
                        retry_after=retry_after,
                        symbol=sym,
                        details=text if text else None,
                    )

                text = await resp.text()
                raise BinanceRestError(
                    message=f"Error en endpoint de Binance ({status})",
                    code="BINANCE_UPSTREAM_ERROR",
                    status_code=status,
                    symbol=sym,
                    details=text if text else None,
                )
        except (BinanceRestError, UnsupportedSymbolError):
            raise
        except TimeoutError as e:
            err_msg = str(e).strip()
            formatted_sec = f"{self.timeout_sec:.1f}"
            details = (
                f"Timeout después de {formatted_sec} segundos"
                if not err_msg
                else f"Timeout: {err_msg}"
            )
            raise BinanceRestError(
                message="Tiempo de espera agotado al conectar con Binance Futures",
                code="BINANCE_GATEWAY_TIMEOUT",
                status_code=504,
                symbol=sym,
                details=details,
            ) from e
        except aiohttp.ClientError as e:
            err_msg = str(e).strip()
            details = f"{type(e).__name__}: {err_msg}".rstrip(": ")
            raise BinanceRestError(
                message="Error de conexión de red con Binance Futures",
                code="BINANCE_CONNECTION_ERROR",
                status_code=503,
                symbol=sym,
                details=details if details else None,
            ) from e

    async def get_open_interest(self, symbol: str) -> tuple[float, int]:
        """Consulta el Open Interest actual y timestamp del contrato.

        Endpoint: GET /fapi/v1/openInterest?symbol=...
        Retorna: (open_interest_float, time_ms)
        """
        sym = self.validate_symbol(symbol)
        data = await self._request("/fapi/v1/openInterest", params={"symbol": sym})
        try:
            oi = float(data["openInterest"])
            time_ms = int(data["time"])
            return oi, time_ms
        except (KeyError, ValueError, TypeError) as e:
            raise BinanceRestError(
                message="Formato no válido en respuesta de openInterest",
                code="BINANCE_MALFORMED_RESPONSE",
                status_code=502,
                symbol=sym,
                details=f"Error al procesar openInterest: {type(e).__name__}: {e}",
            ) from e

    async def get_premium_index(self, symbol: str) -> tuple[float, int]:
        """Consulta el precio de marca y timestamp del contrato.

        Endpoint: GET /fapi/v1/premiumIndex?symbol=...
        Retorna: (mark_price_float, time_ms)
        """
        sym = self.validate_symbol(symbol)
        data = await self._request("/fapi/v1/premiumIndex", params={"symbol": sym})
        try:
            mark_price = float(data["markPrice"])
            time_ms = int(data["time"])
            return mark_price, time_ms
        except (KeyError, ValueError, TypeError) as e:
            raise BinanceRestError(
                message="Formato no válido en respuesta de premiumIndex",
                code="BINANCE_MALFORMED_RESPONSE",
                status_code=502,
                symbol=sym,
                details=f"Error al procesar premiumIndex: {type(e).__name__}: {e}",
            ) from e

    async def get_global_long_short_ratio(
        self, symbol: str, ttl_sec: float | None = None
    ) -> tuple[float, float, int]:
        """Consulta el ratio global de cuentas Long/Short en Binance Futures con caché.

        Endpoint: GET /futures/data/globalLongShortAccountRatio?symbol=...&period=5m&limit=1
        Retorna: (long_account_ratio, short_account_ratio, timestamp_ms)
        """
        sym = self.validate_symbol(symbol)
        effective_ttl = self.cache_ttl_sec if ttl_sec is None else ttl_sec
        now = self.clock()
        if effective_ttl > 0 and sym in self._ratio_cache:
            long_acc, short_acc, ts, fetched_at = self._ratio_cache[sym]
            if now - fetched_at < effective_ttl:
                return long_acc, short_acc, ts

        data = await self._request(
            "/futures/data/globalLongShortAccountRatio",
            params={"symbol": sym, "period": "5m", "limit": "1"},
            expected_type=list,
        )
        try:
            if not isinstance(data, list) or len(data) == 0:
                raise ValueError(f"Lista vacía o formato inválido: {data}")
            item = data[0]
            long_acc = float(item["longAccount"])
            short_acc = float(item["shortAccount"])
            ts = int(item["timestamp"])
            self._ratio_cache[sym] = (long_acc, short_acc, ts, now)
            return long_acc, short_acc, ts
        except (KeyError, ValueError, TypeError) as e:
            raise BinanceRestError(
                message="Formato no válido en respuesta de globalLongShortAccountRatio",
                code="BINANCE_MALFORMED_RESPONSE",
                status_code=502,
                symbol=sym,
                details=f"Error al procesar longShortRatio: {type(e).__name__}: {e}",
            ) from e

    async def get_market_data(
        self,
        symbol: str,
        ttl_sec: float | None = None,
    ) -> BinanceMarketData:
        """Consulta openInterest y premiumIndex con soporte de caché TTL y single-flight en memoria."""
        sym = self.validate_symbol(symbol)
        effective_ttl = self.cache_ttl_sec if ttl_sec is None else ttl_sec
        now = self.clock()

        if effective_ttl > 0 and sym in self._market_data_cache:
            cached_data, fetched_at = self._market_data_cache[sym]
            age = now - fetched_at
            if age < effective_ttl:
                return BinanceMarketData(
                    symbol=cached_data.symbol,
                    mark_price=cached_data.mark_price,
                    open_interest=cached_data.open_interest,
                    open_interest_time=cached_data.open_interest_time,
                    premium_index_time=cached_data.premium_index_time,
                    source=cached_data.source,
                    cached=True,
                    data_age_sec=round(age, 2),
                    long_account_ratio=cached_data.long_account_ratio,
                    short_account_ratio=cached_data.short_account_ratio,
                )

        # Single-flight: sincronización para peticiones concurrentes del mismo símbolo
        lock = self._get_fetch_lock(sym)
        async with lock:
            now = self.clock()
            if effective_ttl > 0 and sym in self._market_data_cache:
                cached_data, fetched_at = self._market_data_cache[sym]
                age = now - fetched_at
                if age < effective_ttl:
                    return BinanceMarketData(
                        symbol=cached_data.symbol,
                        mark_price=cached_data.mark_price,
                        open_interest=cached_data.open_interest,
                        open_interest_time=cached_data.open_interest_time,
                        premium_index_time=cached_data.premium_index_time,
                        source=cached_data.source,
                        cached=True,
                        data_age_sec=round(age, 2),
                    )

            # Si falla la llamada upstream, la excepción se propaga y la caché NO se actualiza (no-caché para errores)
            (oi, oi_time), (mark_price, pi_time) = await asyncio.gather(
                self.get_open_interest(sym),
                self.get_premium_index(sym),
            )
            data = BinanceMarketData(
                symbol=sym,
                mark_price=mark_price,
                open_interest=oi,
                open_interest_time=oi_time,
                premium_index_time=pi_time,
                source="live",
                cached=False,
                data_age_sec=0.0,
            )
            self._market_data_cache[sym] = (data, now)
            return data
