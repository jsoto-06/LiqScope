"""Pruebas unitarias para el cliente REST de Binance Futures USDⓈ-M (Fase 4)."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock

import aiohttp
import pytest

from liqscope.connectors.binance_rest import (
    BinanceFuturesRestClient,
    BinanceMarketData,
    BinanceRateLimitError,
    BinanceRestError,
    UnsupportedSymbolError,
)


class MockResponse:
    """Mock de respuesta HTTP de aiohttp para tests unitarios."""

    def __init__(
        self,
        status: int = 200,
        json_data: Any = None,
        text_data: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status = status
        self._json_data = json_data
        self._text_data = text_data
        self.headers = headers or {}

    async def json(self) -> Any:
        return self._json_data

    async def text(self) -> str:
        return self._text_data

    async def __aenter__(self) -> MockResponse:
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


def test_symbol_validation_and_unsupported_error() -> None:
    """Verifica que solo se admitan BTCUSDT y ETHUSDT y que el error tenga formato unificado."""
    client = BinanceFuturesRestClient()
    assert client.validate_symbol("BTCUSDT") == "BTCUSDT"
    assert client.validate_symbol("btcusdt") == "BTCUSDT"
    assert client.validate_symbol("ETHUSDT") == "ETHUSDT"
    assert client.validate_symbol(" ethusdt ") == "ETHUSDT"

    with pytest.raises(UnsupportedSymbolError) as exc_info:
        client.validate_symbol("SOLUSDT")

    err = exc_info.value
    assert err.symbol == "SOLUSDT"
    assert err.status_code == 400
    assert err.source == "live"
    assert err.code == "UNSUPPORTED_SYMBOL"
    assert "BTCUSDT" in err.message
    assert err.to_dict() == {
        "error": {
            "code": "UNSUPPORTED_SYMBOL",
            "message": err.message,
            "source": "live",
            "symbol": "SOLUSDT",
            "details": f"Supported symbols: {sorted(['BTCUSDT', 'ETHUSDT'])}",
        }
    }


@pytest.mark.asyncio
async def test_get_open_interest_success() -> None:
    """Verifica la consulta exitosa de openInterest."""
    fake_json = {
        "symbol": "BTCUSDT",
        "openInterest": "95448.751",
        "time": 1729630000000,
    }

    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.get.return_value = MockResponse(status=200, json_data=fake_json)
    mock_session.closed = False

    client = BinanceFuturesRestClient(session=mock_session)
    oi, time_ms = await client.get_open_interest("BTCUSDT")

    assert oi == 95448.751
    assert time_ms == 1729630000000
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_get_premium_index_success() -> None:
    """Verifica la consulta exitosa de premiumIndex (markPrice)."""
    fake_json = {
        "symbol": "BTCUSDT",
        "markPrice": "81498.90000000",
        "time": 1729630000000,
    }

    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.get.return_value = MockResponse(status=200, json_data=fake_json)
    mock_session.closed = False

    client = BinanceFuturesRestClient(session=mock_session)
    mark_price, time_ms = await client.get_premium_index("BTCUSDT")

    assert mark_price == 81498.90
    assert time_ms == 1729630000000


@pytest.mark.asyncio
async def test_get_market_data_concurrent() -> None:
    """Verifica la consulta coordinada concurrente de ambos endpoints."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False

    def side_effect(url: str, params: dict[str, str]) -> MockResponse:
        if "openInterest" in url:
            return MockResponse(
                status=200,
                json_data={"symbol": "BTCUSDT", "openInterest": "95448.751", "time": 1729630000000},
            )
        return MockResponse(
            status=200,
            json_data={"symbol": "BTCUSDT", "markPrice": "81498.90", "time": 1729630005000},
        )

    mock_session.get.side_effect = side_effect

    client = BinanceFuturesRestClient(session=mock_session)
    data: BinanceMarketData = await client.get_market_data("BTCUSDT")

    assert data.symbol == "BTCUSDT"
    assert data.mark_price == 81498.90
    assert data.open_interest == 95448.751
    assert data.open_interest_time == 1729630000000
    assert data.premium_index_time == 1729630005000
    assert data.source == "live"


@pytest.mark.asyncio
async def test_rate_limit_errors_429_and_418() -> None:
    """Verifica la captura de 429 y 418 con extracción de cabecera Retry-After."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False

    # Caso 429 con Retry-After
    mock_session.get.return_value = MockResponse(
        status=429,
        text_data="Too many requests",
        headers={"Retry-After": "45"},
    )
    client = BinanceFuturesRestClient(session=mock_session)

    with pytest.raises(BinanceRateLimitError) as exc_info:
        await client.get_open_interest("BTCUSDT")

    err = exc_info.value
    assert err.status_code == 429
    assert err.retry_after == 45
    assert err.source == "live"
    assert err.code == "BINANCE_RATE_LIMIT_EXCEEDED"
    assert err.to_dict()["error"]["retry_after"] == 45

    # Caso 418 IP auto-banned sin Retry-After numérico
    mock_session.get.return_value = MockResponse(
        status=418,
        text_data="IP banned until further notice",
        headers={},
    )
    with pytest.raises(BinanceRateLimitError) as exc_418:
        await client.get_premium_index("ETHUSDT")

    assert exc_418.value.status_code == 418
    assert exc_418.value.code == "BINANCE_IP_BANNED"
    assert exc_418.value.retry_after is None
    assert "retry_after" not in exc_418.value.to_dict()["error"]


@pytest.mark.asyncio
async def test_unexpected_format_and_http_errors() -> None:
    """Verifica respuestas no dict, errores 400 y 500 y campos malformados."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False

    client = BinanceFuturesRestClient(session=mock_session)

    # Respuesta no diccionario
    mock_session.get.return_value = MockResponse(status=200, json_data=["not", "a", "dict"])
    with pytest.raises(BinanceRestError) as exc_json:
        await client.get_open_interest("BTCUSDT")
    assert "no dict" in exc_json.value.message

    # Error HTTP 400
    mock_session.get.return_value = MockResponse(status=400, text_data="Bad Request")
    with pytest.raises(BinanceRestError) as exc_400:
        await client.get_open_interest("BTCUSDT")
    assert exc_400.value.status_code == 400

    # Error HTTP 500
    mock_session.get.return_value = MockResponse(status=500, text_data="Internal Server Error")
    with pytest.raises(BinanceRestError) as exc_500:
        await client.get_premium_index("BTCUSDT")
    assert exc_500.value.status_code == 500

    # Respuesta 200 pero campos faltantes o inválidos
    mock_session.get.return_value = MockResponse(
        status=200,
        json_data={"symbol": "BTCUSDT", "openInterest": "not-a-float"},
    )
    with pytest.raises(BinanceRestError) as exc_malformed:
        await client.get_open_interest("BTCUSDT")
    assert exc_malformed.value.status_code == 502

    mock_session.get.return_value = MockResponse(
        status=200,
        json_data={"symbol": "BTCUSDT", "missingMarkPrice": True},
    )
    with pytest.raises(BinanceRestError) as exc_malformed_pi:
        await client.get_premium_index("BTCUSDT")
    assert exc_malformed_pi.value.status_code == 502


@pytest.mark.asyncio
async def test_network_and_timeout_errors() -> None:
    """Verifica la traducción de Timeout y errores de conexión a BinanceRestError."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False

    # Timeout
    mock_session.get.side_effect = TimeoutError("Connection timed out")
    client = BinanceFuturesRestClient(session=mock_session)

    with pytest.raises(BinanceRestError) as exc_timeout:
        await client.get_open_interest("BTCUSDT")
    assert exc_timeout.value.status_code == 504
    assert exc_timeout.value.code == "BINANCE_GATEWAY_TIMEOUT"
    assert "agotado" in exc_timeout.value.message
    assert not exc_timeout.value.message.endswith(": ")

    # Connection error
    mock_session.get.side_effect = aiohttp.ClientConnectionError("Host unreachable")
    with pytest.raises(BinanceRestError) as exc_conn:
        await client.get_premium_index("BTCUSDT")
    assert exc_conn.value.status_code == 503
    assert exc_conn.value.code == "BINANCE_CONNECTION_ERROR"
    assert "Error de conexión de red" in exc_conn.value.message


@pytest.mark.asyncio
async def test_session_lifecycle_and_context_manager() -> None:
    """Verifica que el context manager abra y cierre la sesión interna correctamente."""
    async with BinanceFuturesRestClient() as client:
        assert client._session is not None
        assert not client._session.closed

    assert client._session.closed

    # Con sesión externa, close no la cierra
    external_session = MagicMock(spec=aiohttp.ClientSession)
    external_session.closed = False
    client_ext = BinanceFuturesRestClient(session=external_session)
    await client_ext.close()
    external_session.close.assert_not_called()


@pytest.mark.parametrize("invalid_timeout", [0.0, -1.0, -5.0])
def test_binance_client_invalid_timeout_raises_value_error(invalid_timeout: float) -> None:
    """Verifica que un timeout <= 0 en el cliente REST lance ValueError al inicializarse."""
    with pytest.raises(ValueError) as exc_info:
        BinanceFuturesRestClient(timeout_sec=invalid_timeout)
    assert "estrictamente positivo" in str(exc_info.value)


@pytest.mark.asyncio
async def test_market_data_cache_hit_and_clear() -> None:
    """Verifica que la segunda llamada dentro del TTL use la caché y clear_cache la reinicie usando reloj inyectado."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False
    fake_json_oi = {"symbol": "BTCUSDT", "openInterest": "95000.0", "time": 1729630000000}
    fake_json_pi = {"symbol": "BTCUSDT", "markPrice": "80000.0", "time": 1729630000000}

    def side_effect(url: str, params: dict[str, str]) -> MockResponse:
        if "openInterest" in url:
            return MockResponse(status=200, json_data=fake_json_oi)
        return MockResponse(status=200, json_data=fake_json_pi)

    mock_session.get.side_effect = side_effect
    BinanceFuturesRestClient.clear_cache()

    # Reloj inyectado determinista sin time.sleep
    current_time = 1000.0

    def mock_clock() -> float:
        return current_time

    client = BinanceFuturesRestClient(session=mock_session, cache_ttl_sec=10.0, clock=mock_clock)

    # 1. Primera llamada (t=1000.0): cache miss -> 2 peticiones salientes
    d1 = await client.get_market_data("BTCUSDT")
    assert d1.cached is False
    assert d1.data_age_sec == 0.0
    assert mock_session.get.call_count == 2

    # 2. Segunda llamada con reloj avanzado (t=1003.5): cache hit dentro de TTL (10s) -> 0 peticiones adicionales
    current_time = 1003.5
    d2 = await client.get_market_data("BTCUSDT")
    assert d2.cached is True
    assert d2.data_age_sec == 3.5
    assert mock_session.get.call_count == 2

    # 3. Limpiar caché -> siguiente llamada es cache miss -> 2 peticiones adicionales (total 4)
    BinanceFuturesRestClient.clear_cache()
    d3 = await client.get_market_data("BTCUSDT")
    assert d3.cached is False
    assert d3.data_age_sec == 0.0
    assert mock_session.get.call_count == 4

    # 4. Avanzar reloj más allá de TTL (t=1015.0 > 10.0s) -> cache miss -> 2 peticiones adicionales (total 6)
    current_time = 1015.0
    d_exp = await client.get_market_data("BTCUSDT")
    assert d_exp.cached is False
    assert d_exp.data_age_sec == 0.0
    assert mock_session.get.call_count == 6


@pytest.mark.asyncio
async def test_market_data_cache_ttl_expiration() -> None:
    """Verifica expiración precisa de TTL y conteo exacto de peticiones salientes por llamada sin time.sleep."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False
    fake_json_oi = {"symbol": "BTCUSDT", "openInterest": "95000.0", "time": 1729630000000}
    fake_json_pi = {"symbol": "BTCUSDT", "markPrice": "80000.0", "time": 1729630000000}

    def side_effect(url: str, params: dict[str, str]) -> MockResponse:
        if "openInterest" in url:
            return MockResponse(status=200, json_data=fake_json_oi)
        return MockResponse(status=200, json_data=fake_json_pi)

    mock_session.get.side_effect = side_effect
    BinanceFuturesRestClient.clear_cache()

    # Reloj inyectado determinista sin time.sleep
    simulated_now = 5000.0

    def mock_clock() -> float:
        return simulated_now

    client = BinanceFuturesRestClient(session=mock_session, cache_ttl_sec=10.0, clock=mock_clock)

    # Llamada 1 (t=5000.0): Miss inicial -> 2 peticiones salientes
    d1 = await client.get_market_data("BTCUSDT")
    assert d1.cached is False
    assert d1.data_age_sec == 0.0
    assert mock_session.get.call_count == 2

    # Llamada 2 (t=5004.5): Dentro de TTL (10.0s) -> 0 peticiones salientes adicionales (total 2)
    simulated_now = 5004.5
    d2 = await client.get_market_data("BTCUSDT")
    assert d2.cached is True
    assert d2.data_age_sec == 4.5
    assert mock_session.get.call_count == 2

    # Llamada 3 (t=5011.0): TTL expirado (>10.0s) -> 2 peticiones salientes adicionales (total 4)
    simulated_now = 5011.0
    d3 = await client.get_market_data("BTCUSDT")
    assert d3.cached is False
    assert d3.data_age_sec == 0.0
    assert mock_session.get.call_count == 4


@pytest.mark.asyncio
async def test_market_data_cache_single_flight_concurrent_10() -> None:
    """Verifica coalescencia single-flight: 10 llamadas concurrentes generan exactamente 2 peticiones salientes."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False
    fake_json_oi = {"symbol": "BTCUSDT", "openInterest": "95000.0", "time": 1729630000000}
    fake_json_pi = {"symbol": "BTCUSDT", "markPrice": "80000.0", "time": 1729630000000}

    async def delayed_side_effect(url: str, params: dict[str, str]) -> MockResponse:
        await asyncio.sleep(0.02)  # Simula latencia para solapar las 10 llamadas concurrentes
        if "openInterest" in url:
            return MockResponse(status=200, json_data=fake_json_oi)
        return MockResponse(status=200, json_data=fake_json_pi)

    # Convertir get en callable asíncrono con context manager MockResponse
    class AsyncMockResponse(MockResponse):
        async def __aenter__(self) -> AsyncMockResponse:
            await asyncio.sleep(0.02)
            return self

    def async_side_effect(url: str, params: dict[str, str]) -> AsyncMockResponse:
        if "openInterest" in url:
            return AsyncMockResponse(status=200, json_data=fake_json_oi)
        return AsyncMockResponse(status=200, json_data=fake_json_pi)

    mock_session.get.side_effect = async_side_effect
    BinanceFuturesRestClient.clear_cache()
    client = BinanceFuturesRestClient(session=mock_session, cache_ttl_sec=5.0)

    # 10 tareas concurrentes solicitando el mismo símbolo en paralelo
    tasks = [client.get_market_data("BTCUSDT") for _ in range(10)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 10
    for r in results:
        assert r.symbol == "BTCUSDT"
        assert r.mark_price == 80000.0
        assert r.open_interest == 95000.0

    # Verificación crítica: Exactamente 2 peticiones salientes a Binance para las 10 llamadas (1 OI + 1 MarkPrice)
    assert mock_session.get.call_count == 2
    cached_hits = sum(1 for r in results if r.cached is True)
    assert cached_hits >= 9


@pytest.mark.asyncio
async def test_market_data_cache_error_not_cached() -> None:
    """Verifica que respuestas de error upstream (502, 504, 429) no se almacenen en caché."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False

    call_index = 0

    def error_then_success_effect(url: str, params: dict[str, str]) -> MockResponse:
        nonlocal call_index
        call_index += 1
        if call_index == 1:
            # Primer intento falla con error HTTP 502 de upstream
            return MockResponse(status=502, text_data="Bad Gateway from Binance")
        if "openInterest" in url:
            return MockResponse(
                status=200,
                json_data={"symbol": "BTCUSDT", "openInterest": "95000.0", "time": 1729630000000},
            )
        return MockResponse(
            status=200,
            json_data={"symbol": "BTCUSDT", "markPrice": "80000.0", "time": 1729630000000},
        )

    mock_session.get.side_effect = error_then_success_effect
    BinanceFuturesRestClient.clear_cache()
    client = BinanceFuturesRestClient(session=mock_session, cache_ttl_sec=5.0)

    # 1. Llamada fallida: debe lanzar BinanceRestError
    with pytest.raises(BinanceRestError) as exc_info:
        await client.get_market_data("BTCUSDT")
    assert exc_info.value.status_code == 502
    assert mock_session.get.call_count == 2

    # 2. Verificar que la caché quedó COMPLETAMENTE VACÍA (no-caché para errores)
    assert "BTCUSDT" not in BinanceFuturesRestClient._market_data_cache

    # 3. Llamada posterior recuperada: debe ejecutar peticiones frescas y tener éxito
    d_recovered = await client.get_market_data("BTCUSDT")
    assert d_recovered.symbol == "BTCUSDT"
    assert d_recovered.cached is False
    assert d_recovered.data_age_sec == 0.0
    # Se realizaron 2 peticiones adicionales (total 3: 1 fallida + 2 recuperadas)
    assert mock_session.get.call_count == 4
    assert "BTCUSDT" in BinanceFuturesRestClient._market_data_cache


@pytest.mark.asyncio
async def test_global_long_short_ratio_success_and_cache() -> None:
    """Verifica consulta exitosa de ratio global y funcionamiento de su caché determinista."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False
    fake_ratio_data = [
        {
            "symbol": "BTCUSDT",
            "longAccount": "0.7790",
            "shortAccount": "0.2210",
            "longShortRatio": "3.5249",
            "timestamp": 1729630000000,
        }
    ]
    mock_session.get.return_value = MockResponse(status=200, json_data=fake_ratio_data)
    BinanceFuturesRestClient.clear_cache()

    clock_time = 1000.0
    client = BinanceFuturesRestClient(
        session=mock_session, cache_ttl_sec=10.0, clock=lambda: clock_time
    )

    # 1. Miss inicial
    long_r, short_r, ts = await client.get_global_long_short_ratio("BTCUSDT")
    assert long_r == 0.7790
    assert short_r == 0.2210
    assert ts == 1729630000000
    assert mock_session.get.call_count == 1

    # 2. Hit en caché dentro de TTL
    clock_time = 1005.0
    long_r2, short_r2, ts2 = await client.get_global_long_short_ratio("BTCUSDT")
    assert (long_r2, short_r2, ts2) == (0.7790, 0.2210, 1729630000000)
    assert mock_session.get.call_count == 1

    # 3. Expiración de TTL
    clock_time = 1015.0
    long_r3, short_r3, ts3 = await client.get_global_long_short_ratio("BTCUSDT")
    assert (long_r3, short_r3, ts3) == (0.7790, 0.2210, 1729630000000)
    assert mock_session.get.call_count == 2


@pytest.mark.asyncio
async def test_global_long_short_ratio_malformed_and_empty() -> None:
    """Verifica manejo de listas vacías o respuestas con claves faltantes."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    mock_session.closed = False
    BinanceFuturesRestClient.clear_cache()
    client = BinanceFuturesRestClient(session=mock_session)

    # Lista vacía
    mock_session.get.return_value = MockResponse(status=200, json_data=[])
    with pytest.raises(BinanceRestError) as exc_empty:
        await client.get_global_long_short_ratio("BTCUSDT")
    assert exc_empty.value.status_code == 502

    # Clave faltante o tipo inválido
    mock_session.get.return_value = MockResponse(
        status=200, json_data=[{"symbol": "BTCUSDT", "wrongKey": "123"}]
    )
    with pytest.raises(BinanceRestError) as exc_key:
        await client.get_global_long_short_ratio("BTCUSDT")
    assert exc_key.value.status_code == 502
