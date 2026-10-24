"""Pruebas unitarias para el cliente REST de Binance Futures USDⓈ-M (Fase 4)."""

from __future__ import annotations

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
    assert "BTCUSDT" in err.message
    assert err.to_dict() == {
        "error": err.message,
        "status_code": 400,
        "source": "live",
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
    assert err.to_dict()["retry_after"] == 45

    # Caso 418 IP auto-banned sin Retry-After numérico
    mock_session.get.return_value = MockResponse(
        status=418,
        text_data="IP banned until further notice",
        headers={},
    )
    with pytest.raises(BinanceRateLimitError) as exc_418:
        await client.get_premium_index("ETHUSDT")

    assert exc_418.value.status_code == 418
    assert exc_418.value.retry_after is None
    assert "retry_after" not in exc_418.value.to_dict()


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

    # Connection error
    mock_session.get.side_effect = aiohttp.ClientConnectionError("Host unreachable")
    with pytest.raises(BinanceRestError) as exc_conn:
        await client.get_premium_index("BTCUSDT")
    assert exc_conn.value.status_code == 503


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
