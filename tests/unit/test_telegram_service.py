"""Tests unitarios para el servicio interactivo de Telegram (TelegramBotService)."""

from __future__ import annotations

import pytest

from liqscope.config import Settings
from liqscope.models.common import Environment
from liqscope.services.telegram_bot import TelegramBotService


@pytest.fixture
def bot_service() -> TelegramBotService:
    """Instancia del servicio de Telegram para pruebas con configuración aislada."""
    cfg = Settings(
        env=Environment.TEST,
        telegram_bot_token="123456:TEST_TOKEN",
        telegram_chat_id="1068166949",
    )
    return TelegramBotService(settings=cfg)


@pytest.mark.asyncio
async def test_process_command_help(bot_service: TelegramBotService) -> None:
    """Verifica respuesta del comando /help o /start."""
    resp = await bot_service.process_command("/help", {"first_name": "Joy"})
    assert "LiqScope Radar Terminal" in resp
    assert "/btc" in resp
    assert "/muros" in resp


@pytest.mark.asyncio
async def test_process_command_simular_empty(bot_service: TelegramBotService) -> None:
    """Verifica que /simular sin argumentos devuelva la guía de uso."""
    resp = await bot_service.process_command("/simular", {})
    assert "Calculadora de Liquidación MMR" in resp
    assert "/simular" in resp


@pytest.mark.asyncio
async def test_process_command_simular_valid(bot_service: TelegramBotService) -> None:
    """Verifica que /simular calcule el precio de liquidación correctamente."""
    resp = await bot_service.process_command("/simular 74500 50 long", {})
    assert "SIMULADOR DE LIQUIDACIÓN MMR" in resp
    assert "LONG" in resp
    assert "Precio de Liquidación" in resp
    assert "73," in resp  # Precio estimado alrededor de 73,382.50


@pytest.mark.asyncio
async def test_process_command_unknown(bot_service: TelegramBotService) -> None:
    """Verifica que un texto libre devuelva el saludo y sugerencia de comandos."""
    resp = await bot_service.process_command("hola que tal", {})
    assert "Soy el bot de <b>LiqScope</b>" in resp
    assert "/btc" in resp
