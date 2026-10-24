"""Tests de integración para la API REST del mapa de calor (/api/v1/heatmap)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from liqscope.api.app import create_app
from liqscope.api.routes.heatmap import get_binance_client
from liqscope.config import Settings
from liqscope.connectors.binance_rest import (
    BinanceFuturesRestClient,
    BinanceMarketData,
    BinanceRateLimitError,
    BinanceRestError,
)
from liqscope.models.common import Environment
from liqscope.models.heatmap import DEFAULT_DISCLAIMER

P_MARK = 81498.90
OI_BTC = 95448.751
TOTAL_OI_USD = round(OI_BTC * P_MARK, 2)  # 7,778,968,212.87 USD


@pytest.fixture
def test_client() -> TestClient:
    """Fixture que instancia TestClient con configuración de test."""
    cfg = Settings(env=Environment.TEST)
    app = create_app(settings=cfg)
    return TestClient(app)


def test_health_check(test_client: TestClient) -> None:
    """Verifica que /health responda 200 con el estado del entorno."""
    resp = test_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "env": "test"}


def test_get_heatmap_btc_live_success_and_invariants(test_client: TestClient) -> None:
    """Verifica la consulta exitosa sin filtros de BTCUSDT con datos en vivo simulados."""
    mock_market_data = BinanceMarketData(
        symbol="BTCUSDT",
        mark_price=P_MARK,
        open_interest=OI_BTC,
        open_interest_time=1729630000000,
        premium_index_time=1729630005000,
        source="live",
    )

    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.return_value = mock_market_data

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp.status_code == 200
        data = resp.json()

        assert data["symbol"] == "BTCUSDT"
        assert data["current_price"] == P_MARK
        assert data["total_open_interest_usd"] == pytest.approx(TOTAL_OI_USD, abs=0.01)
        assert data["visible_bin_volume_usd"] == pytest.approx(TOTAL_OI_USD, abs=0.02)
        assert data["coverage_pct"] == pytest.approx(100.0, abs=0.01)
        assert data["source"] == "live"
        assert data["assumed_long_ratio"] == 0.50
        assert data["disclaimer"] == DEFAULT_DISCLAIMER
        assert data["is_complete"] is True

        assert len(data["bins"]) == 10
        for b in data["bins"]:
            assert b["origin"] == "modeled"
            assert b["coverage"] == "na"
    finally:
        app.dependency_overrides.clear()


def test_get_heatmap_btc_filtered_45_percent(test_client: TestClient) -> None:
    """Verifica el filtrado de rango [79000, 83000] con exactamente 45.0% de coverage."""
    mock_market_data = BinanceMarketData(
        symbol="BTCUSDT",
        mark_price=P_MARK,
        open_interest=OI_BTC,
        open_interest_time=1729630000000,
        premium_index_time=1729630005000,
        source="live",
    )

    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.return_value = mock_market_data

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT?min_price=79000&max_price=83000")
        assert resp.status_code == 200
        data = resp.json()

        # Debe contener exactamente 5 bins
        assert len(data["bins"]) == 5
        expected_vol = 3500535695.79
        assert data["visible_bin_volume_usd"] == pytest.approx(expected_vol, abs=0.01)
        assert data["coverage_pct"] == pytest.approx(45.0, abs=0.01)

        # Consistencia estricta: visible_bin_volume_usd / total_open_interest_usd * 100
        expected_pct = (data["visible_bin_volume_usd"] / data["total_open_interest_usd"]) * 100.0
        assert data["coverage_pct"] == pytest.approx(expected_pct, abs=0.01)
    finally:
        app.dependency_overrides.clear()


def test_get_heatmap_ethusdt_success(test_client: TestClient) -> None:
    """Verifica la consulta exitosa para el segundo símbolo admitido (ETHUSDT)."""
    mock_market_data = BinanceMarketData(
        symbol="ETHUSDT",
        mark_price=2650.0,
        open_interest=350000.0,
        open_interest_time=1729630000000,
        premium_index_time=1729630005000,
        source="live",
    )

    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.return_value = mock_market_data

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/ETHUSDT")
        assert resp.status_code == 200
        data = resp.json()
        assert data["symbol"] == "ETHUSDT"
        assert data["current_price"] == 2650.0
        assert data["total_open_interest_usd"] == 2650.0 * 350000.0
    finally:
        app.dependency_overrides.clear()


def test_get_heatmap_demo_source(test_client: TestClient) -> None:
    """Verifica la respuesta generada con source=demo para BTC y ETH sin llamada externa."""
    resp_btc = test_client.get("/api/v1/heatmap/BTCUSDT?source=demo")
    assert resp_btc.status_code == 200
    data_btc = resp_btc.json()
    assert data_btc["source"] == "demo"
    assert data_btc["symbol"] == "BTCUSDT"

    resp_eth = test_client.get("/api/v1/heatmap/ETHUSDT?source=demo")
    assert resp_eth.status_code == 200
    data_eth = resp_eth.json()
    assert data_eth["source"] == "demo"
    assert data_eth["symbol"] == "ETHUSDT"


def test_unsupported_symbol_returns_400(test_client: TestClient) -> None:
    """Verifica que pares no autorizados (ej. SOLUSDT) devuelvan 400 y formato unificado."""
    resp = test_client.get("/api/v1/heatmap/SOLUSDT")
    assert resp.status_code == 400
    data = resp.json()
    assert data["status_code"] == 400
    assert data["source"] == "live"
    assert "SOLUSDT" in data["error"]

    resp_demo = test_client.get("/api/v1/heatmap/DOGEUSDT?source=demo")
    assert resp_demo.status_code == 400
    data_demo = resp_demo.json()
    assert data_demo["source"] == "demo"


def test_invalid_range_min_greater_than_max(test_client: TestClient) -> None:
    """Verifica que min_price > max_price devuelva HTTP 400."""
    resp = test_client.get("/api/v1/heatmap/BTCUSDT?min_price=85000&max_price=80000")
    assert resp.status_code == 400
    data = resp.json()
    assert data["status_code"] == 400
    assert "no puede ser mayor" in data["error"]
    assert data["source"] == "live"


def test_rate_limit_429_forwarded(test_client: TestClient) -> None:
    """Verifica que un error HTTP 429 de Binance reenvíe Retry-After y estructura unificada."""
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.side_effect = BinanceRateLimitError(
        message="Too many requests to Binance",
        status_code=429,
        retry_after=60,
    )

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp.status_code == 429
        assert resp.headers.get("retry-after") == "60"
        data = resp.json()
        assert data["status_code"] == 429
        assert data["retry_after"] == 60
        assert data["source"] == "live"
    finally:
        app.dependency_overrides.clear()


def test_rate_limit_418_forwarded(test_client: TestClient) -> None:
    """Verifica que un error HTTP 418 de Binance reenvíe el código 418 unificado."""
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.side_effect = BinanceRateLimitError(
        message="IP auto-banned",
        status_code=418,
    )

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp.status_code == 418
        data = resp.json()
        assert data["status_code"] == 418
        assert data["source"] == "live"
    finally:
        app.dependency_overrides.clear()


def test_binance_rest_error_and_unexpected_crash(test_client: TestClient) -> None:
    """Verifica el reenvío de errores 502 por fallas en Binance y 500 por excepciones no previstas."""
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.side_effect = BinanceRestError(
        message="Binance 502 Bad Gateway",
        status_code=502,
    )

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp.status_code == 502
        data = resp.json()
        assert data["status_code"] == 502
        assert data["source"] == "live"

        # Excepción genérica inesperada
        mock_client.get_market_data.side_effect = RuntimeError("Fatal connection loss")
        resp_crash = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp_crash.status_code == 500
        data_crash = resp_crash.json()
        assert data_crash["status_code"] == 500
        assert "Fatal connection loss" in data_crash["error"]
    finally:
        app.dependency_overrides.clear()


def test_custom_parameters_bin_size_and_ratio(test_client: TestClient) -> None:
    """Verifica que bin_size y assumed_long_ratio personalizados se apliquen correctamente."""
    resp = test_client.get(
        "/api/v1/heatmap/BTCUSDT?bin_size=100.0&assumed_long_ratio=0.70&source=demo"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["bin_size"] == 100.0
    assert data["assumed_long_ratio"] == 0.70


@pytest.mark.asyncio
async def test_get_binance_client_dependency() -> None:
    """Verifica que la función dependiente de FastAPI get_binance_client funcione como generador asíncrono."""
    settings = Settings(env=Environment.TEST)
    gen = get_binance_client(settings=settings)
    client = await anext(gen)
    assert isinstance(client, BinanceFuturesRestClient)
    with pytest.raises(StopAsyncIteration):
        await anext(gen)


def test_create_app_without_cors() -> None:
    """Verifica la inicialización de la app sin orígenes CORS."""
    cfg = Settings(env=Environment.TEST, cors_origins=[])
    app = create_app(settings=cfg)
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
