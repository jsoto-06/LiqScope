"""Pruebas de integración para las rutas y servicios de liquidaciones forzadas reales (REKT Ticker)."""

from __future__ import annotations

import pytest
from starlette.testclient import TestClient

from liqscope.api.app import create_app
from liqscope.config import Settings
from liqscope.models.liquidation import LiquidationEvent, LiquidationStats
from liqscope.services.liquidation_feed import get_liquidation_feed_service


@pytest.fixture
def client() -> TestClient:
    settings = Settings(env="test")
    app = create_app(settings)
    return TestClient(app)


def test_get_recent_liquidations_endpoint(client: TestClient) -> None:
    """Verifica que /api/v1/liquidations/recent responda con 200 y estructura esperada."""
    resp = client.get("/api/v1/liquidations/recent?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "count" in data
    assert "events" in data
    assert "stats" in data
    assert isinstance(data["events"], list)


def test_get_liquidation_stats_endpoint(client: TestClient) -> None:
    """Verifica que /api/v1/liquidations/stats retorne métricas acumuladas."""
    resp = client.get("/api/v1/liquidations/stats")
    assert resp.status_code == 200
    stats = resp.json()
    assert "total_count" in stats
    assert "total_volume_usd" in stats
    assert "whale_count" in stats


def test_liquidation_feed_processing_and_whale_classification() -> None:
    """Verifica el procesamiento de eventos crudos de Binance y detección de ballenas."""
    feed = get_liquidation_feed_service()

    # Simular mensaje crudo de liquidación de Long en BTC (> $100K = Ballena)
    mock_payload = {
        "e": "forceOrder",
        "E": 1731160800000,
        "o": {
            "s": "BTCUSDT",
            "S": "SELL",  # Long liquidado
            "o": "LIMIT",
            "q": "2.000",
            "p": "75000.00",
            "ap": "75000.00",
            "X": "FILLED",
            "T": 1731160800000,
        },
    }

    feed._process_message(mock_payload)

    recent = feed.get_recent(symbol="BTCUSDT", limit=1)
    assert len(recent) >= 1
    ev = recent[0]
    assert ev.symbol == "BTCUSDT"
    assert ev.liquidated_side == "LONG"
    assert ev.volume_usd == 150000.0
    assert ev.is_whale is True
    assert ev.is_mega_whale is False

    stats = feed.get_stats()
    assert stats.whale_count >= 1
    assert stats.long_volume_usd >= 150000.0
