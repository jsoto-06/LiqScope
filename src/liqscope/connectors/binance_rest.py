"""Cliente REST asíncrono para Binance Futures USDⓈ-M (Fase 4).

Endpoints utilizados (Solo lectura pública):
- GET /fapi/v1/openInterest?symbol={symbol}
- GET /fapi/v1/premiumIndex?symbol={symbol}

Alcance estricto: Únicamente BTCUSDT y ETHUSDT.
Gestión de errores: HTTP 429/418 (Rate Limit) y respuestas unificadas con campo source.
"""

from __future__ import annotations

import asyncio
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


class BinanceRestError(Exception):
    """Excepción base para errores de la API REST de Binance."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        source: str = "live",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.source = source

    def to_dict(self) -> dict[str, Any]:
        """Estructura normalizada de error con campo source uniforme."""
        return {
            "error": self.message,
            "status_code": self.status_code,
            "source": self.source,
        }


class BinanceRateLimitError(BinanceRestError):
    """Excepción específica cuando se supera el límite de tasa de Binance (HTTP 429 o 418)."""

    def __init__(
        self,
        message: str = "Binance rate limit exceeded",
        status_code: int = 429,
        retry_after: int | None = None,
        source: str = "live",
    ) -> None:
        super().__init__(message=message, status_code=status_code, source=source)
        self.retry_after = retry_after

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        if self.retry_after is not None:
            data["retry_after"] = self.retry_after
        return data


class UnsupportedSymbolError(BinanceRestError):
    """Excepción lanzada cuando se solicita un par fuera del alcance de la Fase 4."""

    def __init__(
        self,
        symbol: str,
        status_code: int = 400,
        source: str = "live",
    ) -> None:
        message = (
            f"Símbolo no soportado en esta fase: '{symbol}'. "
            f"Solo se admiten: {', '.join(sorted(SUPPORTED_SYMBOLS))}."
        )
        super().__init__(message=message, status_code=status_code, source=source)
        self.symbol = symbol


class BinanceFuturesRestClient:
    """Cliente HTTP asíncrono para consultar Open Interest y Mark Price en Binance Futures."""

    def __init__(
        self,
        base_url: str = "https://fapi.binance.com",
        session: aiohttp.ClientSession | None = None,
        timeout_sec: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._session = session
        self._owns_session = session is None
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)

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

    async def _request(self, path: str, params: dict[str, str]) -> dict[str, Any]:
        """Ejecuta una petición GET y gestiona códigos de respuesta de Binance."""
        session = await self._ensure_session()
        url = f"{self.base_url}{path}"

        try:
            async with session.get(url, params=params) as resp:
                status = resp.status
                if status == 200:
                    data = await resp.json()
                    if not isinstance(data, dict):
                        raise BinanceRestError(
                            f"Respuesta inesperada de Binance (no dict): {data}",
                            status_code=status,
                        )
                    return data

                # Detección de Rate Limits HTTP 429 / 418
                if status in (429, 418):
                    retry_header = resp.headers.get("Retry-After")
                    retry_after = (
                        int(retry_header) if retry_header and retry_header.isdigit() else None
                    )
                    text = await resp.text()
                    raise BinanceRateLimitError(
                        message=f"Límite de peticiones de Binance alcanzado (HTTP {status}): {text}",
                        status_code=status,
                        retry_after=retry_after,
                    )

                text = await resp.text()
                raise BinanceRestError(
                    message=f"Error en endpoint de Binance ({status}): {text}",
                    status_code=status,
                )
        except (BinanceRestError, UnsupportedSymbolError):
            raise
        except TimeoutError as e:
            raise BinanceRestError(
                message=f"Timeout de red al conectar con Binance: {e}",
                status_code=504,
            ) from e
        except aiohttp.ClientError as e:
            raise BinanceRestError(
                message=f"Error de conexión de red con Binance: {e}",
                status_code=503,
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
                f"Formato no válido en respuesta de openInterest: {data}",
                status_code=502,
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
                f"Formato no válido en respuesta de premiumIndex: {data}",
                status_code=502,
            ) from e

    async def get_market_data(self, symbol: str) -> BinanceMarketData:
        """Consulta de forma concurrente openInterest y premiumIndex para el símbolo."""
        sym = self.validate_symbol(symbol)
        (oi, oi_time), (mark_price, pi_time) = await asyncio.gather(
            self.get_open_interest(sym),
            self.get_premium_index(sym),
        )
        return BinanceMarketData(
            symbol=sym,
            mark_price=mark_price,
            open_interest=oi,
            open_interest_time=oi_time,
            premium_index_time=pi_time,
            source="live",
        )
