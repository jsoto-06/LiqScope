"""Cliente asíncrono para el envío de alertas mediante la API de Telegram Bot."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp


class TelegramClient:
    """Cliente HTTP asíncrono para interactuar con la API de Telegram Bot."""

    BASE_URL = "https://api.telegram.org"

    def __init__(
        self,
        bot_token: str,
        chat_id: str,
        timeout_sec: float = 5.0,
    ) -> None:
        self.bot_token = bot_token.strip()
        self.chat_id = chat_id.strip()
        self.timeout = aiohttp.ClientTimeout(total=timeout_sec)

    @property
    def is_configured(self) -> bool:
        """Determina si las credenciales mínimas están presentes."""
        return bool(self.bot_token and self.chat_id)

    async def send_message_to(
        self,
        chat_id: str | int,
        text: str,
        parse_mode: str = "HTML",
    ) -> tuple[bool, str]:
        """Envía un mensaje a un chat específico."""
        if not self.bot_token:
            return False, "Bot Token no configurado."

        url = f"{self.BASE_URL}/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": str(chat_id),
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as resp:
                    resp_json: dict[str, Any] = await resp.json()
                    if resp.status == 200 and resp_json.get("ok"):
                        return True, "Mensaje enviado exitosamente a Telegram."

                    error_desc = resp_json.get("description", f"HTTP {resp.status}")
                    return False, f"Telegram API Error: {error_desc}"
        except asyncio.TimeoutError:
            return False, "Timeout al conectar con los servidores de Telegram."
        except aiohttp.ClientError as err:
            return False, f"Error de red al conectar con Telegram: {err}"
        except Exception as err:
            return False, f"Error inesperado al enviar mensaje: {err}"

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
    ) -> tuple[bool, str]:
        """Envía un mensaje de texto al chat_id configurado por defecto."""
        if not self.chat_id:
            return False, "Chat ID no configurado."
        return await self.send_message_to(self.chat_id, text, parse_mode=parse_mode)

    async def get_updates(
        self,
        offset: int | None = None,
        timeout_sec: int = 10,
    ) -> list[dict[str, Any]]:
        """Obtiene las actualizaciones entrantes de Telegram mediante polling."""
        if not self.bot_token:
            return []

        url = f"{self.BASE_URL}/bot{self.bot_token}/getUpdates"
        params: dict[str, Any] = {"timeout": timeout_sec}
        if offset is not None:
            params["offset"] = offset

        client_timeout = aiohttp.ClientTimeout(total=timeout_sec + 5)
        try:
            async with aiohttp.ClientSession(timeout=client_timeout) as session:
                async with session.get(url, params=params) as resp:
                    resp_json: dict[str, Any] = await resp.json()
                    if resp.status == 200 and resp_json.get("ok"):
                        return resp_json.get("result", [])
                    return []
        except Exception:
            return []

    async def send_liquidation_alert(
        self,
        title: str,
        symbol: str,
        price: float,
        delta_pct: float,
        volume_usd: float,
        leverage: str = "50x",
        side: str = "SHORT",
        tactical_tip: str = "",
    ) -> tuple[bool, str]:
        """Formatea y envía una alerta de liquidación estructurada."""
        delta_sign = "+" if delta_pct >= 0 else ""
        side_emoji = "🔴" if side.upper() == "SHORT" else "🟢"
        vol_str = f"${volume_usd / 1e6:.1f}M USD" if volume_usd > 0 else "N/A"

        msg = (
            f"🚨 <b>LIQSCOPE RADAR ALERT</b>\n"
            f"{side_emoji} <b>{symbol.upper()} | {title}</b>\n\n"
            f"🎯 <b>Nivel Objetivo:</b> <code>${price:,.2f}</code> (<b>{delta_sign}{delta_pct:.2f}%</b>)\n"
            f"💰 <b>Volumen Estimado:</b> <b>{vol_str}</b>\n"
            f"⚡ <b>Dirección / Palanca:</b> {side.upper()} {leverage}\n"
        )

        if tactical_tip:
            msg += f"\n💡 <b>Playbook Táctico:</b>\n<i>{tactical_tip}</i>\n"

        msg += "\n⏱ <i>LiqScope Telemetry • Binance Futures Live Sync</i>"

        return await self.send_message(msg, parse_mode="HTML")

    async def test_connection(self) -> tuple[bool, str]:
        """Envía un mensaje de prueba para verificar que el Bot Token y Chat ID sean válidos."""
        test_msg = (
            "🤖 <b>LiqScope — Conexión con Telegram Exitosa</b>\n\n"
            "El radar de telemetría de liquidaciones está vinculado a este chat.\n"
            "Recibirás avisos en tiempo real cuando el Mark Price se aproxime a clústeres masivos."
        )
        return await self.send_message(test_msg, parse_mode="HTML")

    async def get_latest_chat_id(self) -> tuple[str | None, str]:
        """Consulta getUpdates para detectar automáticamente el chat_id del último usuario."""
        if not self.bot_token:
            return None, "Bot Token no configurado."

        url = f"{self.BASE_URL}/bot{self.bot_token}/getUpdates"
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as resp:
                    resp_json: dict[str, Any] = await resp.json()
                    if not resp_json.get("ok"):
                        return None, f"Telegram API: {resp_json.get('description', 'Error desconocido')}"

                    results = resp_json.get("result", [])
                    if not results:
                        return (
                            None,
                            "No se detectaron mensajes en el bot. Abre Telegram, busca @criptobtctrader_bot y pulsa 'Iniciar' primero.",
                        )

                    for update in reversed(results):
                        msg = (
                            update.get("message")
                            or update.get("channel_post")
                            or update.get("my_chat_member", {}).get("chat")
                        )
                        if isinstance(msg, dict):
                            chat = msg.get("chat") if "chat" in msg else msg
                            if chat and "id" in chat:
                                name = chat.get("first_name") or chat.get("title") or chat["id"]
                                return str(chat["id"]), f"Chat detectado para '{name}'"

                    return None, "No se encontró información de chat en las actualizaciones recientes."
        except asyncio.TimeoutError:
            return None, "Timeout al conectar con Telegram."
        except Exception as err:
            return None, f"Error al consultar Telegram: {err}"
