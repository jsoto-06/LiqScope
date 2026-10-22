"""Tests unitarios para el conector de Binance Futures con fixtures grabados."""

import asyncio
import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from liqscope.connectors.base import ConnectionStatus
from liqscope.connectors.binance import BinanceFuturesConnector
from liqscope.models.common import DataOrigin, Exchange, PositionSide, TradeSide
from liqscope.models.liquidation import LiquidationEvent
from liqscope.models.market import Trade


@pytest.fixture
def recorded_messages() -> dict[str, dict[str, Any]]:
    """Carga los mensajes grabados oficiales para pruebas sin red."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "binance_messages.json"
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
        return cast(dict[str, dict[str, Any]], data)


def test_parse_agg_trade_buyer_maker(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el parseo de aggTrade cuando el comprador es maker (venta agresiva -> AGGRESSIVE_SELL)."""
    msg = recorded_messages["valid_agg_trade_buyer_maker"]
    trade = BinanceFuturesConnector.parse_agg_trade(msg)

    assert trade is not None
    assert trade.exchange == Exchange.BINANCE
    assert trade.symbol == "BTCUSDT"
    assert trade.price == 68520.10
    assert trade.quantity == 0.450
    assert trade.side == TradeSide.AGGRESSIVE_SELL
    assert trade.trade_id == "12345678"


def test_parse_agg_trade_buyer_taker(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el parseo de aggTrade cuando el comprador es taker (compra agresiva -> AGGRESSIVE_BUY)."""
    msg = recorded_messages["valid_agg_trade_buyer_taker"]
    trade = BinanceFuturesConnector.parse_agg_trade(msg)

    assert trade is not None
    assert trade.exchange == Exchange.BINANCE
    assert trade.symbol == "BTCUSDT"
    assert trade.price == 68525.00
    assert trade.quantity == 1.250
    assert trade.side == TradeSide.AGGRESSIVE_BUY
    assert trade.trade_id == "12345679"


def test_parse_force_order_sell(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el parseo de forceOrder con orden SELL (liquidación de posición LONG)."""
    msg = recorded_messages["valid_force_order_sell"]
    liq = BinanceFuturesConnector.parse_force_order(msg)

    assert liq is not None
    assert liq.exchange == Exchange.BINANCE
    assert liq.symbol == "BTCUSDT"
    assert liq.side == PositionSide.LONG
    assert liq.price == 68100.00
    assert liq.quantity == 2.500
    assert liq.filled_quantity == 2.500
    assert liq.usd_volume == 68100.00 * 2.500
    assert liq.origin == DataOrigin.ESTIMATED


def test_parse_force_order_buy(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el parseo de forceOrder con orden BUY (liquidación de posición SHORT)."""
    msg = recorded_messages["valid_force_order_buy"]
    liq = BinanceFuturesConnector.parse_force_order(msg)

    assert liq is not None
    assert liq.exchange == Exchange.BINANCE
    assert liq.symbol == "BTCUSDT"
    assert liq.side == PositionSide.SHORT
    assert liq.price == 68900.00
    assert liq.quantity == 1.800
    assert liq.filled_quantity == 1.800
    assert liq.usd_volume == 68900.00 * 1.800


def test_parse_malformed_messages_returns_none(
    recorded_messages: dict[str, dict[str, Any]],
) -> None:
    """Verifica que mensajes con campos faltantes o valores inválidos sean descartados."""
    msg_missing = recorded_messages["malformed_missing_fields"]
    assert BinanceFuturesConnector.parse_agg_trade(msg_missing) is None

    msg_neg = recorded_messages["malformed_negative_price"]
    assert BinanceFuturesConnector.parse_agg_trade(msg_neg) is None

    # Probar forceOrder malformado
    assert BinanceFuturesConnector.parse_force_order({}) is None
    assert BinanceFuturesConnector.parse_force_order({"o": {"p": "-100"}}) is None


@pytest.mark.asyncio
async def test_handle_raw_message_dispatches_events(
    recorded_messages: dict[str, dict[str, Any]],
) -> None:
    """Verifica que handle_raw_message despache trades y liquidaciones a callbacks registrados."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")

    emitted_trades: list[Trade] = []
    emitted_liqs: list[LiquidationEvent] = []

    async def on_trade(trade: Trade) -> None:
        emitted_trades.append(trade)

    async def on_liq(evt: LiquidationEvent) -> None:
        emitted_liqs.append(evt)

    connector.register_trade_handler(on_trade)
    connector.register_liquidation_handler(on_liq)

    # Enviar trade crudo
    raw_trade = json.dumps(recorded_messages["valid_agg_trade_buyer_maker"])
    await connector.handle_raw_message(raw_trade)

    # Enviar liquidación cruda
    raw_liq = json.dumps(recorded_messages["valid_force_order_sell"])
    await connector.handle_raw_message(raw_liq)

    # Enviar payload combinado {"stream": "btcusdt@aggTrade", "data": {...}}
    combined_payload = {
        "stream": "btcusdt@aggTrade",
        "data": recorded_messages["valid_agg_trade_buyer_taker"],
    }
    await connector.handle_raw_message(json.dumps(combined_payload))

    # Enviar evento no manejado (ej. kline)
    await connector.handle_raw_message(json.dumps({"e": "kline", "s": "BTCUSDT"}))

    # Enviar JSON corrupto (no debe romper la ejecución)
    await connector.handle_raw_message("INVALID_NOT_JSON{")

    # Enviar JSON no-dict
    await connector.handle_raw_message(json.dumps([1, 2, 3]))

    assert len(emitted_trades) == 2
    assert emitted_trades[0].price == 68520.10
    assert emitted_trades[0].side == TradeSide.AGGRESSIVE_SELL
    assert emitted_trades[1].price == 68525.00
    assert emitted_trades[1].side == TradeSide.AGGRESSIVE_BUY

    assert len(emitted_liqs) == 1
    assert emitted_liqs[0].price == 68100.00


def test_connector_stream_url() -> None:
    """Verifica que la URL del stream se construya correctamente según la especificación de Binance."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    url = connector._get_stream_url()
    assert "fstream.binance.com/ws/stream?streams=btcusdt@aggTrade/btcusdt@forceOrder" in url


@pytest.mark.asyncio
async def test_connector_stop_cancels_running_task() -> None:
    """Verifica que stop() cancele una tarea activa en ejecución y suprima CancelledError."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")

    async def infinite_mock_loop() -> None:
        while True:
            await asyncio.sleep(0.01)

    connector._running = True
    connector._task = asyncio.create_task(infinite_mock_loop())

    await connector.stop()
    assert connector._running is False
    assert connector._task.done()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connector_run_loop_handles_ws_close_messages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que mensajes WSMsgType.CLOSE cierren el stream sin error."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector.settings.ws_reconnect_min_delay_sec = 0.01

    class MockCloseWS:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "MockCloseWS":
            return self

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                connector._running = False
                yield MagicMock(type=aiohttp.WSMsgType.CLOSE, data="")

            return gen()

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()
    mock_session.ws_connect.return_value = MockCloseWS()
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: mock_session)

    await connector.start()
    await asyncio.sleep(0.02)
    await connector.stop()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connector_run_loop_empty_ws_stream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que un stream WS vacío termine la iteración limpiamente (línea 206->232)."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector.settings.ws_reconnect_min_delay_sec = 0.01

    class MockEmptyWS:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "MockEmptyWS":
            return self

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                connector._running = False
                if False:
                    yield None

            return gen()

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()
    mock_session.ws_connect.return_value = MockEmptyWS()
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: mock_session)

    await connector.start()
    await asyncio.sleep(0.02)
    await connector.stop()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connector_start_idempotent() -> None:
    """Verifica que llamar start() cuando ya está corriendo no cree tareas duplicadas."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector._running = True
    await connector.start()
    assert connector._running is True


@pytest.mark.asyncio
async def test_connector_stop_with_active_session_and_ws() -> None:
    """Verifica que stop() cierre sockets y sesiones activas limpiamente."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()

    mock_ws = MagicMock()
    mock_ws.closed = False
    mock_ws.close = AsyncMock()

    connector._session = mock_session
    connector._ws = mock_ws

    await connector.stop()
    mock_ws.close.assert_awaited_once()
    mock_session.close.assert_awaited_once()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connector_reconnect_loop_on_client_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Simula una desconexión o fallo en el websocket sin tocar la red exterior."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector.settings.ws_reconnect_min_delay_sec = 0.01
    connector.settings.ws_reconnect_max_delay_sec = 0.02

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()

    calls = 0

    class MockContextManager:
        async def __aenter__(self) -> None:
            nonlocal calls
            calls += 1
            if calls == 1:
                raise aiohttp.ClientError("Simulated network drop")
            connector._running = False
            raise asyncio.CancelledError()

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

    mock_session.ws_connect.return_value = MockContextManager()
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: mock_session)

    await connector.start()
    await asyncio.sleep(0.05)
    await connector.stop()

    assert calls >= 1
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connector_run_loop_processes_ws_stream(
    monkeypatch: pytest.MonkeyPatch,
    recorded_messages: dict[str, dict[str, Any]],
) -> None:
    """Verifica que el bucle procese mensajes TEXT y BINARY del WebSocket y termine limpiamente."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector.settings.ws_reconnect_min_delay_sec = 0.01

    raw_trade = json.dumps(recorded_messages["valid_agg_trade_buyer_maker"])
    raw_liq = json.dumps(recorded_messages["valid_force_order_sell"]).encode("utf-8")

    class MockWS:
        def __init__(self) -> None:
            self.closed = False

        def exception(self) -> Exception | None:
            return None

        async def __aenter__(self) -> "MockWS":
            return self

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                # 1. Enviar mensaje TEXT
                yield MagicMock(type=aiohttp.WSMsgType.TEXT, data=raw_trade)
                # 2. Enviar mensaje BINARY
                yield MagicMock(type=aiohttp.WSMsgType.BINARY, data=raw_liq)
                # 3. Detener el bucle y enviar CLOSE
                connector._running = False
                yield MagicMock(type=aiohttp.WSMsgType.CLOSE, data="")

            return gen()

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()
    mock_session.ws_connect.return_value = MockWS()
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: mock_session)

    emitted: list[Trade] = []

    async def on_trade(trade: Trade) -> None:
        emitted.append(trade)

    connector.register_trade_handler(on_trade)

    await connector.start()
    await asyncio.sleep(0.05)
    await connector.stop()

    assert len(emitted) == 1
    assert emitted[0].price == 68520.10
    assert emitted[0].side == TradeSide.AGGRESSIVE_SELL


@pytest.mark.asyncio
async def test_connector_run_loop_handles_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que una excepción inesperada durante la conexión sea capturada y pase a ERROR."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector.settings.ws_reconnect_min_delay_sec = 0.01
    connector.settings.ws_reconnect_max_delay_sec = 0.02

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()

    class MockFailingContextManager:
        async def __aenter__(self) -> None:
            connector._running = False
            raise RuntimeError("Excepción catastrófica simulada")

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            pass

    mock_session.ws_connect.return_value = MockFailingContextManager()
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: mock_session)

    await connector.start()
    await asyncio.sleep(0.03)
    await connector.stop()

    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connector_run_loop_handles_ws_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que un mensaje de tipo WSMsgType.ERROR rompa el stream y no lance excepciones."""
    connector = BinanceFuturesConnector(symbol="BTCUSDT")
    connector.settings.ws_reconnect_min_delay_sec = 0.01

    class MockErrorWS:
        def __init__(self) -> None:
            self.closed = False

        def exception(self) -> Exception | None:
            return RuntimeError("WS Protocol Error")

        async def __aenter__(self) -> "MockErrorWS":
            return self

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                connector._running = False
                yield MagicMock(type=aiohttp.WSMsgType.ERROR, data="")

            return gen()

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()
    mock_session.ws_connect.return_value = MockErrorWS()
    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: mock_session)

    await connector.start()
    await asyncio.sleep(0.02)
    await connector.stop()

    assert connector.status == ConnectionStatus.DISCONNECTED
