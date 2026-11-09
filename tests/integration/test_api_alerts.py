"""Tests de integración para la API de alertas y conector Telegram (/api/v1/alerts)."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from liqscope.api.app import create_app
from liqscope.config import Settings
from liqscope.models.common import Environment


@pytest.fixture
def alert_client() -> TestClient:
    """Instancia TestClient para pruebas de rutas de alertas."""
    cfg = Settings(env=Environment.TEST)
    app = create_app(settings=cfg)
    return TestClient(app)


def test_telegram_status_unconfigured(alert_client: TestClient) -> None:
    """Verifica el endpoint de estado cuando Telegram no está configurado."""
    resp = alert_client.get("/api/v1/alerts/telegram/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "configured" in data
    assert data["configured"] is False
    assert data["alerts_enabled"] is False


def test_telegram_test_missing_params(alert_client: TestClient) -> None:
    """Verifica que /telegram/test devuelva 400 si faltan credenciales."""
    resp = alert_client.post(
        "/api/v1/alerts/telegram/test",
        json={"bot_token": "", "chat_id": ""},
    )
    assert resp.status_code == 400
    assert "Se requiere Bot Token y Chat ID" in resp.json()["detail"]


@patch("liqscope.api.routes.alerts.TelegramClient.test_connection")
def test_telegram_test_success(mock_test_conn: AsyncMock, alert_client: TestClient) -> None:
    """Verifica llamada exitosa de test_connection mockeando la red."""
    mock_test_conn.return_value = (True, "Mensaje de prueba enviado exitosamente.")

    resp = alert_client.post(
        "/api/v1/alerts/telegram/test",
        json={"bot_token": "123456:FAKE_TOKEN", "chat_id": "987654321"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Mensaje de prueba enviado" in data["message"]


@patch("liqscope.api.routes.alerts.TelegramClient.send_liquidation_alert")
def test_telegram_send_alert_success(
    mock_send_alert: AsyncMock, alert_client: TestClient
) -> None:
    """Verifica despacho exitoso de una alerta de liquidación a Telegram."""
    mock_send_alert.return_value = (True, "Alerta enviada exitosamente.")

    payload = {
        "bot_token": "123456:FAKE_TOKEN",
        "chat_id": "987654321",
        "title": "Muro Principal MAX LIQ",
        "symbol": "BTCUSDT",
        "price": 82450.0,
        "delta_pct": 1.15,
        "volume_usd": 840_000_000.0,
        "leverage": "50x",
        "side": "SHORT",
        "tactical_tip": "Posible Short Squeeze",
    }
    resp = alert_client.post("/api/v1/alerts/telegram/send", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Alerta enviada" in data["message"]
