"""Servicio de Bot interactivo de Telegram para LiqScope.

Ejecuta un loop en segundo plano mediante Long Polling para responder
a comandos de los usuarios (/btc, /eth, /muros, /riesgo, /simular, /ayuda)
utilizando los datos reales de Binance Futures y el motor de liquidación.
"""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from liqscope.config import Settings
from liqscope.connectors.binance_rest import (
    BinanceFuturesRestClient,
    BinanceMarketData,
)
from liqscope.connectors.telegram import TelegramClient
from liqscope.engine.aggregator import build_heatmap_snapshot
from liqscope.engine.formulas import calculate_approximate_liquidation_price
from liqscope.models.common import PositionSide
from liqscope.models.heatmap import HeatmapSnapshot

logger = logging.getLogger("liqscope.services.telegram_bot")


class TelegramBotService:
    """Servicio interactivo de Telegram que procesa comandos mediante Long Polling."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = TelegramClient(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id,
            timeout_sec=settings.http_request_timeout_sec,
        )
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    @property
    def is_running(self) -> bool:
        """Indica si el worker en segundo plano está activo."""
        return self._task is not None and not self._task.done()

    def start(self) -> None:
        """Inicia el worker de polling si el bot token está configurado."""
        if not self.client.bot_token:
            logger.info("Telegram Bot Token no configurado. Servicio interactivo omitido.")
            return

        if self.is_running:
            return

        self._stop_event.clear()
        self._task = asyncio.create_task(self._polling_loop(), name="liqscope_telegram_bot")
        logger.info("Servicio interactivo de Telegram iniciado exitosamente.")

    async def stop(self) -> None:
        """Detiene de forma ordenada el worker de polling."""
        if not self._task:
            return

        self._stop_event.set()
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        finally:
            self._task = None
            logger.info("Servicio interactivo de Telegram detenido.")

    async def _polling_loop(self) -> None:
        """Bucle principal de escucha de mensajes entrantes mediante getUpdates."""
        last_offset: int | None = None
        logger.info("Iniciando escucha de comandos en Telegram...")

        while not self._stop_event.is_set():
            try:
                updates = await self.client.get_updates(offset=last_offset, timeout_sec=5)
                for update in updates:
                    update_id = update.get("update_id")
                    if update_id is not None:
                        last_offset = update_id + 1

                    msg = update.get("message")
                    if not msg:
                        continue

                    chat = msg.get("chat", {})
                    chat_id = chat.get("id")
                    text = (msg.get("text") or "").strip()

                    if chat_id and text:
                        asyncio.create_task(
                            self._handle_and_reply(chat_id, text, chat),
                            name=f"tg_msg_{update_id}",
                        )

            except asyncio.CancelledError:
                break
            except Exception as err:
                logger.warning("Error en el bucle de polling de Telegram: %s", err)
                await asyncio.sleep(2.0)

    async def _handle_and_reply(
        self,
        chat_id: int | str,
        text: str,
        chat: dict[str, Any],
    ) -> None:
        """Procesa un comando y despacha la respuesta al chat correspondiente."""
        try:
            reply_text = await self.process_command(text, chat)
            if reply_text:
                await self.client.send_message_to(chat_id, reply_text, parse_mode="HTML")
        except Exception as err:
            logger.error("Error al procesar comando '%s': %s", text, err)
            error_msg = (
                "⚠️ <b>Error al procesar la solicitud</b>\n"
                "Ha ocurrido un problema al consultar la telemetría. Inténtalo de nuevo en unos segundos."
            )
            await self.client.send_message_to(chat_id, error_msg, parse_mode="HTML")

    async def process_command(self, text: str, chat: dict[str, Any]) -> str:
        """Enruta el comando recibido a su handler especializado."""
        clean_text = text.strip()
        cmd_lower = clean_text.lower()
        parts = clean_text.split()
        first_token = parts[0].lower() if parts else ""

        # Quitar sufijo @nombre_de_bot si fue enviado en un grupo (ej: /btc@criptobtctrader_bot)
        if "@" in first_token:
            first_token = first_token.split("@")[0]

        if first_token in {"/start", "/help", "/ayuda"}:
            first_name = chat.get("first_name", "Trader")
            return self._help_message(first_name)

        if first_token in {"/btc", "/bitcoin"}:
            return await self._symbol_telemetry("BTCUSDT")

        if first_token in {"/eth", "/ethereum"}:
            return await self._symbol_telemetry("ETHUSDT")

        if first_token in {"/muros", "/clusters", "/heatmap"}:
            sym = "ETHUSDT" if len(parts) > 1 and "eth" in parts[1].lower() else "BTCUSDT"
            return await self._walls_summary(sym)

        if first_token in {"/exchanges", "/global", "/mercado"}:
            sym = "ETHUSDT" if len(parts) > 1 and "eth" in parts[1].lower() else "BTCUSDT"
            return await self._exchanges_summary(sym)

        if first_token in {"/rekt", "/liquidaciones", "/feed"}:
            return self._rekt_summary()

        if first_token in {"/riesgo", "/analisis", "/radar"}:
            return await self._risk_diagnosis()

        if first_token == "/simular":
            return self._simulate_liquidation(parts[1:])

        # Mensaje por defecto cuando no es un comando reconocido
        return (
            "👋 ¡Hola! Soy el bot de <b>LiqScope</b>.\n\n"
            "Escribe uno de estos comandos para obtener telemetría en tiempo real:\n"
            "• <b>/btc</b> — Precio, OI y ratios de Bitcoin\n"
            "• <b>/eth</b> — Telemetría de Ethereum\n"
            "• <b>/muros</b> — Muros de liquidación más densos\n"
            "• <b>/riesgo</b> — Diagnóstico de sentimiento y volatilidad\n"
            "• <b>/simular</b> — Calculadora de liquidación\n"
            "• <b>/ayuda</b> — Menú completo de comandos"
        )

    def _help_message(self, user_name: str) -> str:
        """Genera el mensaje interactivo de bienvenida y catálogo de comandos."""
        return (
            f"🤖 <b>LiqScope Radar Terminal</b>\n\n"
            f"¡Hola {user_name}! Estoy conectado al motor analítico de <b>LiqScope</b> "
            f"con liquidez agregada de <b>Binance, Bybit, Hyperliquid y Kraken</b>.\n\n"
            f"📋 <b>Comandos Disponibles:</b>\n\n"
            f"⚡ <b>/btc</b> — Telemetría global de Bitcoin (Mark VWAP, OI Agregado, Ratio L/S).\n"
            f"⚡ <b>/eth</b> — Telemetría global de Ethereum.\n"
            f"⚡ <b>/rekt</b> — Feed de liquidaciones forzadas reales en directo y ballenas.\n"
            f"🌐 <b>/exchanges</b> — Desglose de Open Interest entre los 4 exchanges.\n"
            f"🧱 <b>/muros</b> — Muestra los 4 muros de liquidación más densos cerca del precio.\n"
            f"⚖️ <b>/riesgo</b> — Análisis de asimetría y probabilidad de barrido (Sweep).\n"
            f"🧮 <b>/simular &lt;precio&gt; &lt;palanca&gt; &lt;long/short&gt;</b> — Calcula tu precio de liquidación exacto.\n"
            f"   <i>Ejemplo:</i> <code>/simular 74500 50x long</code>\n\n"
            f"🌐 <i>Terminal Web: http://localhost:8000</i>"
        )

    async def _get_live_snapshot(self, symbol: str, exchange: str = "all") -> HeatmapSnapshot:
        """Obtiene una instantánea calculada con datos en vivo agregados de 4 exchanges."""
        from liqscope.connectors.multi_exchange import MultiExchangeAggregator
        agg = MultiExchangeAggregator(
            cache_ttl_sec=self.settings.market_data_cache_ttl_sec,
            timeout_sec=self.settings.http_request_timeout_sec,
        )
        multi_snap = await agg.get_aggregated_snapshot(symbol, target_exchange=exchange)

        bin_size = 50.0 if symbol == "BTCUSDT" else 10.0
        exchange_breakdown = {k: q.open_interest_usd for k, q in multi_snap.exchanges.items()}

        return build_heatmap_snapshot(
            symbol=symbol,
            mark_price=multi_snap.aggregated_mark_price,
            total_open_interest_usd=multi_snap.total_open_interest_usd,
            bin_size=bin_size,
            assumed_long_ratio=multi_snap.long_account_ratio,
            source="live",
            cached=False,
            data_age_sec=0.0,
            long_account_ratio=multi_snap.long_account_ratio,
            short_account_ratio=multi_snap.short_account_ratio,
            ratio_source="live",
            exchange=exchange,
            exchange_breakdown=exchange_breakdown,
        )

    async def _exchanges_summary(self, symbol: str = "BTCUSDT") -> str:
        """Genera el desglose comparativo de Open Interest entre los 4 exchanges."""
        from liqscope.connectors.multi_exchange import MultiExchangeAggregator
        agg = MultiExchangeAggregator(
            cache_ttl_sec=self.settings.market_data_cache_ttl_sec,
            timeout_sec=self.settings.http_request_timeout_sec,
        )
        multi_snap = await agg.get_aggregated_snapshot(symbol, target_exchange="all")

        lines = [
            f"🌐 <b>AGREGACIÓN MULTI-EXCHANGE | {symbol}</b>\n",
            f"💵 <b>Mark VWAP:</b> <code>${multi_snap.aggregated_mark_price:,.2f}</code>",
            f"📊 <b>OI Total Global:</b> <b>${multi_snap.total_open_interest_usd / 1e9:.2f}B USD</b>\n",
            "🏦 <b>Desglose de Liquidez:</b>",
        ]

        emojis = {
            "binance": "🟡",
            "bybit": "🟠",
            "hyperliquid": "🟢",
            "kraken": "🟣",
        }

        for k, q in multi_snap.exchanges.items():
            emo = emojis.get(k, "🔹")
            lines.append(
                f"{emo} <b>{q.display_name}:</b> "
                f"${q.open_interest_usd / 1e6:,.1f}M (<b>{q.share_pct:.1f}%</b>) @ <code>${q.mark_price:,.1f}</code>"
            )

        lines.append("\n💡 <i>Las liquidaciones se calculan sobre la liquidez combinada de los 4 exchanges.</i>")
        return "\n".join(lines)

    def _rekt_summary(self) -> str:
        """Genera el reporte de liquidaciones reales capturadas por el feed WebSocket."""
        from liqscope.services.liquidation_feed import get_liquidation_feed_service
        feed = get_liquidation_feed_service()
        stats = feed.get_stats()
        recent = feed.get_recent(limit=8)

        lines = [
            "⚡ <b>REKT TICKER | LIQUIDACIONES EN VIVO</b>\n",
            f"📊 <b>Total Sesión:</b> {stats.total_count} órdenes | <b>${stats.total_volume_usd / 1e6:,.2f}M USD</b>",
            f"🔴 <b>Longs REKT:</b> ${stats.long_volume_usd / 1e6:,.2f}M ({stats.long_count})",
            f"🟢 <b>Shorts REKT:</b> ${stats.short_volume_usd / 1e6:,.2f}M ({stats.short_count})",
            f"🐳 <b>Ballenas (> $100K):</b> {stats.whale_count} eventos\n",
            "⏱️ <b>Últimas Liquidaciones Ejecutadas:</b>",
        ]

        if not recent:
            lines.append("<i>Capturando ejecuciones de liquidación en el mercado...</i>")
        else:
            for ev in recent:
                icon = "🔴 LONG" if ev.liquidated_side == "LONG" else "🟢 SHORT"
                whale_tag = " 🐳" if ev.is_whale else ""
                vol_str = f"${ev.volume_usd:,.0f}" if ev.volume_usd < 100_000 else f"${ev.volume_usd / 1e3:,.1f}K"
                lines.append(f"• <b>{ev.symbol}</b> {icon}: <code>{vol_str}</code> @ ${ev.avg_price:,.2f}{whale_tag}")

        lines.append("\n🌐 <i>Feed conectado en vivo a Binance Force Orders WebSocket.</i>")
        return "\n".join(lines)

    async def _symbol_telemetry(self, symbol: str) -> str:
        """Genera el reporte de telemetría instantáneo para un símbolo."""
        snapshot = await self._get_live_snapshot(symbol)
        mark = snapshot.current_price

        # Encontrar clúster MAX LIQ
        max_bin = max(snapshot.bins, key=lambda b: b.estimated_volume_usd) if snapshot.bins else None
        max_delta = (((max_bin.price_mid - mark) / mark) * 100) if (max_bin and mark > 0) else 0.0
        delta_sign = "+" if max_delta >= 0 else ""
        is_max_short = max_bin and (max_bin.short_volume_usd > max_bin.long_volume_usd)

        sym_clean = "BTC/USDT" if symbol == "BTCUSDT" else "ETH/USDT"
        precision = 2 if symbol == "ETHUSDT" else 2

        return (
            f"⚡ <b>TELEMETRÍA EN VIVO | {sym_clean}</b>\n\n"
            f"💵 <b>Mark Price:</b> <code>${mark:,.{precision}f}</code>\n"
            f"📊 <b>Open Interest:</b> <b>${snapshot.total_open_interest_usd / 1e6:,.1f}M USD</b>\n"
            f"⚖️ <b>Ratio Cuentas L/S:</b> <b>{snapshot.long_account_ratio * 100:.1f}%</b> Long | "
            f"<b>{snapshot.short_account_ratio * 100:.1f}%</b> Short\n\n"
            f"🎯 <b>Clúster MAX LIQ:</b> <code>${max_bin.price_mid:,.{precision}f}</code> "
            f"({delta_sign}{max_delta:.2f}%)\n"
            f"💰 <b>Volumen Concentrado:</b> <b>${max_bin.estimated_volume_usd / 1e6:,.1f}M USD</b>\n"
            f"⚡ <b>Palanca Dominante:</b> {max_bin.dominant_leverage or 50:.0f}x "
            f"({'Cortos' if is_max_short else 'Largos'})\n\n"
            f"⏱ <i>Binance Futures USDⓈ-M Live Sync</i>"
        )

    async def _walls_summary(self, symbol: str) -> str:
        """Genera el desglose vertical de los muros de liquidación más densos."""
        snapshot = await self._get_live_snapshot(symbol)
        mark = snapshot.current_price
        precision = 2 if symbol == "ETHUSDT" else 0

        shorts = [b for b in snapshot.bins if b.price_mid > mark]
        longs = [b for b in snapshot.bins if b.price_mid < mark]

        shorts.sort(key=lambda b: b.price_mid)  # Más cercanos primero
        longs.sort(key=lambda b: b.price_mid, reverse=True)  # Más cercanos primero

        lines: list[str] = [
            f"🧱 <b>MUROS DE LIQUIDACIÓN | {symbol}</b>\n",
            "🔴 <b>Zonas de Liquidación Short (Arriba):</b>",
        ]

        if shorts:
            for b in shorts[:2]:
                delta = ((b.price_mid - mark) / mark) * 100
                lev = f"{b.dominant_leverage:.0f}x" if b.dominant_leverage else "Multi"
                lines.append(
                    f"• <code>${b.price_mid:,.{precision}f}</code> (+{delta:.2f}%) ➔ "
                    f"<b>${b.estimated_volume_usd / 1e6:.1f}M</b> ({lev})"
                )
        else:
            lines.append("• <i>No hay clústeres densos inmediatos arriba</i>")

        lines.append(f"\n🎯 <b>Mark Actual:</b> <code>${mark:,.2f}</code>\n")
        lines.append("🟢 <b>Zonas de Liquidación Long (Abajo):</b>")

        if longs:
            for b in longs[:2]:
                delta = ((b.price_mid - mark) / mark) * 100
                lev = f"{b.dominant_leverage:.0f}x" if b.dominant_leverage else "Multi"
                lines.append(
                    f"• <code>${b.price_mid:,.{precision}f}</code> ({delta:.2f}%) ➔ "
                    f"<b>${b.estimated_volume_usd / 1e6:.1f}M</b> ({lev})"
                )
        else:
            lines.append("• <i>No hay clústeres densos inmediatos abajo</i>")

        lines.append("\n💡 <i>Escribe /riesgo para ver el diagnóstico de sentimiento.</i>")
        return "\n".join(lines)

    async def _risk_diagnosis(self) -> str:
        """Genera un análisis sintético del entorno de riesgo y sentimiento."""
        snapshot = await self._get_live_snapshot("BTCUSDT")
        mark = snapshot.current_price

        long_pct = snapshot.long_account_ratio * 100
        short_pct = snapshot.short_account_ratio * 100

        max_bin = max(snapshot.bins, key=lambda b: b.estimated_volume_usd) if snapshot.bins else None
        dist_to_max = abs(((max_bin.price_mid - mark) / mark) * 100) if (max_bin and mark > 0) else 5.0

        if dist_to_max <= 1.0:
            risk_level = "🔴 <b>ALTO RIESGO DE BARRIDO INMINENTE</b>"
            action = (
                "El precio se encuentra a menos de 1% del clúster masivo. "
                "Alta propensión a caza de liquidez forzada antes de un giro brusco."
            )
        elif long_pct >= 62.0 or short_pct >= 62.0:
            skew_side = "largos" if long_pct >= 62.0 else "cortos"
            risk_level = "🟡 <b>RIESGO ELEVADO POR ASIMETRÍA</b>"
            action = (
                f"El {max(long_pct, short_pct):.1f}% de las cuentas están en {skew_side}. "
                f"Típicamente los creadores de mercado barren al lado mayoritario."
            )
        else:
            risk_level = "🟢 <b>EQUILIBRIO MODERADO</b>"
            action = "El mercado cotiza en rango sin fricción extrema de liquidaciones inmediatas."

        return (
            f"⚖️ <b>DIAGNÓSTICO DE RIESGO | BTCUSDT</b>\n\n"
            f"Estado: {risk_level}\n\n"
            f"• <b>Mark Price:</b> ${mark:,.2f}\n"
            f"• <b>Distancia al Clúster MAX:</b> {dist_to_max:.2f}%\n"
            f"• <b>Desbalance L/S:</b> {long_pct:.1f}% L / {short_pct:.1f}% S\n\n"
            f"💡 <b>Playbook Táctico:</b>\n<i>{action}</i>"
        )

    def _simulate_liquidation(self, args: list[str]) -> str:
        """Calcula el precio de liquidación aproximado a partir de los argumentos."""
        if not args:
            return (
                "🧮 <b>Calculadora de Liquidación MMR</b>\n\n"
                "<b>Uso:</b> <code>/simular &lt;precio_entrada&gt; &lt;palanca&gt; &lt;long/short&gt;</code>\n\n"
                "<b>Ejemplos:</b>\n"
                "• <code>/simular 74500 50 long</code>\n"
                "• <code>/simular 76000 25 short</code>\n"
                "• <code>/simular 74500 100x</code> (por defecto Long)"
            )

        try:
            raw_price = args[0].replace("$", "").replace(",", "")
            entry_price = float(raw_price)

            raw_lev = args[1].lower().replace("x", "") if len(args) > 1 else "50"
            leverage = float(raw_lev)

            side_str = args[2].lower() if len(args) > 2 else "long"
            side = PositionSide.SHORT if "short" in side_str or "corto" in side_str else PositionSide.LONG

            # MMR aproximado según apalancamiento
            if leverage >= 100:
                mmr = 0.004
            elif leverage >= 50:
                mmr = 0.005
            elif leverage >= 25:
                mmr = 0.010
            elif leverage >= 10:
                mmr = 0.020
            else:
                mmr = 0.040

            liq_price = calculate_approximate_liquidation_price(
                entry_price=entry_price,
                leverage=leverage,
                side=side,
                maintenance_margin_rate=mmr,
            )

            delta_pct = ((liq_price - entry_price) / entry_price) * 100
            buffer_usd = abs(entry_price - liq_price)
            delta_sign = "+" if delta_pct >= 0 else ""

            side_name = "LONG (Compra)" if side == PositionSide.LONG else "SHORT (Venta)"
            side_emoji = "🟢" if side == PositionSide.LONG else "🔴"

            return (
                f"🧮 <b>SIMULADOR DE LIQUIDACIÓN MMR</b>\n\n"
                f"{side_emoji} <b>Dirección:</b> {side_name}\n"
                f"💵 <b>Precio de Entrada:</b> ${entry_price:,.2f}\n"
                f"⚡ <b>Apalancamiento:</b> {leverage:.0f}x (MMR {mmr * 100:.2f}%)\n\n"
                f"💀 <b>Precio de Liquidación:</b> <code>${liq_price:,.2f}</code> "
                f"({delta_sign}{delta_pct:.2f}%)\n"
                f"🛡 <b>Margen de Seguridad:</b> ${buffer_usd:,.2f} USDT\n\n"
                f"💡 <i>Si el precio se mueve ${buffer_usd:,.2f} en tu contra, "
                f"el motor de Binance liquidará la posición.</i>"
            )
        except Exception as err:
            return (
                f"⚠️ <b>Parámetros inválidos</b>\n"
                f"Uso correcto: <code>/simular 74500 50 long</code>\n"
                f"Detalle: {err}"
            )
