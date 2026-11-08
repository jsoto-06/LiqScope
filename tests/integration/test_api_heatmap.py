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


def test_index_dashboard(test_client: TestClient) -> None:
    """Verifica que el dashboard visual responda en / con HTML 200 y temporizador de 2 minutos."""
    resp = test_client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "LiqScope — Liquidation Heatmap" in resp.text
    assert "BTCUSDT" in resp.text
    assert "ETHUSDT" in resp.text
    assert "countdown-text" in resp.text
    assert "AUTO_REFRESH_INTERVAL_SEC = 120" in resp.text


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
    assert "error" in data
    assert data["error"]["code"] == "UNSUPPORTED_SYMBOL"
    assert data["error"]["source"] == "live"
    assert "SOLUSDT" in data["error"]["message"]

    resp_demo = test_client.get("/api/v1/heatmap/DOGEUSDT?source=demo")
    assert resp_demo.status_code == 400
    data_demo = resp_demo.json()
    assert data_demo["error"]["source"] == "demo"
    assert data_demo["error"]["code"] == "UNSUPPORTED_SYMBOL"


def test_invalid_range_min_greater_than_max(test_client: TestClient) -> None:
    """Verifica que min_price > max_price devuelva HTTP 400."""
    resp = test_client.get("/api/v1/heatmap/BTCUSDT?min_price=85000&max_price=80000")
    assert resp.status_code == 400
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "INVALID_PRICE_RANGE"
    assert "no puede ser mayor" in data["error"]["message"]
    assert data["error"]["source"] == "live"


def test_rate_limit_429_forwarded(test_client: TestClient) -> None:
    """Verifica que un error HTTP 429 de Binance reenvíe Retry-After y estructura unificada."""
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.side_effect = BinanceRateLimitError(
        message="Too many requests to Binance",
        code="BINANCE_RATE_LIMIT_EXCEEDED",
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
        assert "error" in data
        assert data["error"]["code"] == "BINANCE_RATE_LIMIT_EXCEEDED"
        assert data["error"]["retry_after"] == 60
        assert data["error"]["source"] == "live"
    finally:
        app.dependency_overrides.clear()


def test_rate_limit_418_forwarded(test_client: TestClient) -> None:
    """Verifica que un error HTTP 418 de Binance reenvíe el código 418 unificado."""
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.side_effect = BinanceRateLimitError(
        message="IP auto-banned",
        code="BINANCE_IP_BANNED",
        status_code=418,
    )

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp.status_code == 418
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "BINANCE_IP_BANNED"
        assert data["error"]["source"] == "live"
    finally:
        app.dependency_overrides.clear()


def test_binance_rest_error_and_unexpected_crash(test_client: TestClient) -> None:
    """Verifica el reenvío de errores 502 por fallas en Binance y 500 por excepciones no previstas."""
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.side_effect = BinanceRestError(
        message="Binance 502 Bad Gateway",
        code="BINANCE_UPSTREAM_ERROR",
        status_code=502,
    )

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        resp = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp.status_code == 502
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "BINANCE_UPSTREAM_ERROR"
        assert data["error"]["source"] == "live"

        # Excepción genérica inesperada
        mock_client.get_market_data.side_effect = RuntimeError("Fatal connection loss")
        resp_crash = test_client.get("/api/v1/heatmap/BTCUSDT")
        assert resp_crash.status_code == 500
        data_crash = resp_crash.json()
        assert "error" in data_crash
        assert data_crash["error"]["code"] == "INTERNAL_SERVER_ERROR"
        assert "Fatal connection loss" in data_crash["error"]["message"]
        assert data_crash["error"]["source"] == "live"
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


def test_live_timeout_against_silent_local_server() -> None:
    """Fuerza un timeout real contra un socket TCP local no bloqueante y verifica respuesta 504 literal."""
    import select
    import socket
    import threading
    import time

    from liqscope.api.routes.heatmap import get_settings

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("127.0.0.1", 0))
    server_sock.listen(1)
    server_sock.setblocking(False)  # Socket explícitamente no bloqueante
    port = server_sock.getsockname()[1]

    connection_accepted = threading.Event()
    stop_event = threading.Event()
    accepted_client_addr: list[tuple[str, int]] = []
    server_errors: list[Exception] = []

    def silent_server() -> None:
        conn: socket.socket | None = None
        try:
            readable, _, _ = select.select([server_sock], [], [], 2.0)
            if readable:
                conn, addr = server_sock.accept()
                accepted_client_addr.append(addr)
                connection_accepted.set()  # Prueba irrefutable de que el servidor aceptó la conexión TCP
                stop_event.wait(timeout=2.0)
        except OSError as exc:
            server_errors.append(exc)
        finally:
            if conn is not None:
                conn.close()
            server_sock.close()

    thread = threading.Thread(target=silent_server, daemon=True)
    thread.start()

    try:
        cfg = Settings(
            env=Environment.TEST,
            binance_rest_url=f"http://127.0.0.1:{port}",
            http_request_timeout_sec=0.2,
        )
        app = create_app(settings=cfg)
        app.dependency_overrides[get_settings] = lambda: cfg
        client = TestClient(app)

        t0 = time.time()
        resp = client.get("/api/v1/heatmap/BTCUSDT?source=live")
        elapsed = time.time() - t0

        # Verificaciones estrictas:
        # 1. El servidor aceptó la conexión TCP (no es conexión rechazada / ECONNREFUSED)
        assert server_errors == [], f"Errores inesperados en socket servidor: {server_errors}"
        assert connection_accepted.is_set(), "El servidor local no llegó a aceptar la conexión TCP"
        assert len(accepted_client_addr) == 1
        # 2. El cliente abortó por timeout (HTTP 504 con código de contrato BINANCE_GATEWAY_TIMEOUT)
        assert resp.status_code == 504
        assert elapsed < 1.0
        data = resp.json()
        assert "error" in data
        assert data["error"]["code"] == "BINANCE_GATEWAY_TIMEOUT"
        assert (
            data["error"]["message"] == "Tiempo de espera agotado al conectar con Binance Futures"
        )
        assert data["error"]["source"] == "live"
        assert data["error"]["symbol"] == "BTCUSDT"
        assert data["error"]["details"] == "Timeout después de 0.2 segundos"
    finally:
        stop_event.set()
        thread.join(timeout=1.0)


def test_heatmap_cache_hit_in_api() -> None:
    """Verifica que llamadas consecutivas a /api/v1/heatmap reflejen cached=True y data_age_sec."""
    BinanceFuturesRestClient.clear_cache()
    mock_market_data = BinanceMarketData(
        symbol="BTCUSDT",
        mark_price=80000.0,
        open_interest=95000.0,
        open_interest_time=1729630000000,
        premium_index_time=1729630005000,
        source="live",
        cached=False,
        data_age_sec=0.0,
    )
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    d_hit = BinanceMarketData(
        symbol="BTCUSDT",
        mark_price=80000.0,
        open_interest=95000.0,
        open_interest_time=1729630000000,
        premium_index_time=1729630005000,
        source="live",
        cached=True,
        data_age_sec=1.2,
    )
    mock_client.get_market_data.side_effect = [mock_market_data, d_hit]

    app = create_app(settings=Settings(env=Environment.TEST))
    app.dependency_overrides[get_binance_client] = lambda: mock_client
    client = TestClient(app)

    try:
        r1 = client.get("/api/v1/heatmap/BTCUSDT")
        assert r1.status_code == 200
        assert r1.json()["cached"] is False
        assert r1.json()["data_age_sec"] == 0.0

        r2 = client.get("/api/v1/heatmap/BTCUSDT")
        assert r2.status_code == 200
        assert r2.json()["cached"] is True
        assert r2.json()["data_age_sec"] == 1.2
    finally:
        app.dependency_overrides.clear()
        BinanceFuturesRestClient.clear_cache()


def test_get_symbols_endpoints(test_client: TestClient) -> None:
    """Verifica que GET /api/v1/symbols devuelva la forma aprobada y no exista alias no versionado."""
    resp = test_client.get("/api/v1/symbols")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0] == {"symbol": "BTCUSDT", "default_bin_size": 50.0}
    assert data[1] == {"symbol": "ETHUSDT", "default_bin_size": 10.0}

    # El alias sin versión /symbols fue eliminado según decisión de arquitectura REST
    resp_unversioned = test_client.get("/symbols")
    assert resp_unversioned.status_code == 404


def test_heatmap_ratio_modes_and_fallback(test_client: TestClient) -> None:
    """Verifica modos de ratio 'live', 'neutral' y fallback en caso de error en ratio."""
    mock_market_data = BinanceMarketData(
        symbol="ETHUSDT",
        mark_price=2200.0,
        open_interest=200000.0,
        open_interest_time=1729630000000,
        premium_index_time=1729630005000,
        source="live",
    )
    mock_client = AsyncMock(spec=BinanceFuturesRestClient)
    mock_client.get_market_data.return_value = mock_market_data
    mock_client.get_global_long_short_ratio.return_value = (0.75, 0.25, 1729630000000)

    app = test_client.app
    assert isinstance(app, FastAPI)
    app.dependency_overrides[get_binance_client] = lambda: mock_client

    try:
        # 1. Modo live: toma el ratio devuelto por Binance (0.75 / 0.25)
        resp_live = test_client.get("/api/v1/heatmap/ETHUSDT?ratio_mode=live")
        assert resp_live.status_code == 200
        d_live = resp_live.json()
        assert d_live["long_account_ratio"] == 0.75
        assert d_live["short_account_ratio"] == 0.25
        assert d_live["assumed_long_ratio"] == 0.75
        assert d_live["ratio_source"] == "live"

        # 2. Modo neutral: fuerza 50.0% / 50.0%
        resp_neutral = test_client.get("/api/v1/heatmap/ETHUSDT?ratio_mode=neutral")
        assert resp_neutral.status_code == 200
        d_neutral = resp_neutral.json()
        assert d_neutral["assumed_long_ratio"] == 0.50
        assert d_neutral["ratio_source"] == "neutral"

        # 3. Fallback: cuando get_global_long_short_ratio falla, se usa (0.50, 0.50) sin romper la API
        mock_client.get_global_long_short_ratio.side_effect = Exception(
            "Binance ratio endpoint error"
        )
        resp_fallback = test_client.get("/api/v1/heatmap/ETHUSDT?ratio_mode=live")
        assert resp_fallback.status_code == 200
        d_fallback = resp_fallback.json()
        assert d_fallback["long_account_ratio"] == 0.50
        assert d_fallback["short_account_ratio"] == 0.50
        assert d_fallback["assumed_long_ratio"] == 0.50
    finally:
        app.dependency_overrides.clear()


def test_manual_dashboard(test_client: TestClient) -> None:
    """Verifica que /manual responda 200 con el manual y guía de usuario."""
    resp = test_client.get("/manual")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "Manual de Usuario" in resp.text
