"""Tests unitarios para el conector de Bybit Linear con fixtures de allLiquidation."""

import asyncio
import json
from pathlib import Path
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from liqscope.config import Settings
from liqscope.connectors.base import ConnectionStatus
from liqscope.connectors.bybit import BybitConnector
from liqscope.models.common import DataCoverage, DataOrigin, Exchange, PositionSide
from liqscope.models.liquidation import LiquidationEvent


@pytest.fixture
def recorded_messages() -> dict[str, dict[str, Any]]:
    """Carga los mensajes grabados de Bybit para pruebas sin red."""
    fixture_path = Path(__file__).parent.parent / "fixtures" / "bybit_messages.json"
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
        return cast(dict[str, dict[str, Any]], data)


def test_parse_official_example_roseusdt(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el parseo del mensaje oficial de ROSEUSDT con S='Sell' (posición SHORT liquidada)."""
    msg = recorded_messages["official_all_liquidation_roseusdt"]
    events = BybitConnector.parse_all_liquidation(msg)

    assert len(events) == 1
    ev = events[0]
    assert ev.exchange == Exchange.BYBIT
    assert ev.symbol == "ROSEUSDT"
    assert ev.side == PositionSide.SHORT
    assert ev.price is None
    assert ev.bankruptcy_price == 0.04499
    assert ev.quantity == 20000.0
    assert ev.filled_quantity == 20000.0
    assert ev.usd_volume == 0.04499 * 20000.0
    assert ev.origin == DataOrigin.OBSERVED
    assert ev.coverage == DataCoverage.COMPLETE
    assert ev.incomplete is False
    assert ev.timestamp.timestamp() == 1739502302.929


def test_parse_synthetic_example_btcusdt(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el parseo sintético con S='Buy' (posición LONG liquidada según la documentación de Bybit)."""
    msg = recorded_messages["synthetic_all_liquidation_btcusdt"]
    events = BybitConnector.parse_all_liquidation(msg)

    assert len(events) == 1
    ev = events[0]
    assert ev.exchange == Exchange.BYBIT
    assert ev.symbol == "BTCUSDT"
    assert ev.side == PositionSide.LONG
    assert ev.price is None
    assert ev.bankruptcy_price == 65000.5
    assert ev.quantity == 1.5
    assert ev.filled_quantity == 1.5
    assert ev.usd_volume == 65000.5 * 1.5
    assert ev.origin == DataOrigin.OBSERVED
    assert ev.coverage == DataCoverage.COMPLETE
    assert ev.incomplete is False
    assert ev.timestamp.timestamp() == 1739502302.929


def test_parse_synthetic_example_ethusdt(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica el procesamiento sintético de múltiples eventos en un único payload."""
    msg = recorded_messages["synthetic_all_liquidation_ethusdt"]
    events = BybitConnector.parse_all_liquidation(msg)

    assert len(events) == 2
    assert events[0].symbol == "ETHUSDT"
    assert events[0].side == PositionSide.LONG
    assert events[0].price is None
    assert events[0].bankruptcy_price == 3200.0
    assert events[0].quantity == 10.0
    assert events[0].origin == DataOrigin.OBSERVED
    assert events[0].coverage == DataCoverage.COMPLETE

    assert events[1].symbol == "ETHUSDT"
    assert events[1].side == PositionSide.SHORT
    assert events[1].price is None
    assert events[1].bankruptcy_price == 3250.0
    assert events[1].quantity == 5.0
    assert events[1].origin == DataOrigin.OBSERVED
    assert events[1].coverage == DataCoverage.COMPLETE


@pytest.mark.asyncio
async def test_disconnection_gap_detection(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica que un corte de conexión active incomplete=True en los eventos emitidos."""
    connector = BybitConnector(symbol="ROSEUSDT")
    assert not connector.has_disconnection_gap

    # Sin corte: incomplete es False
    msg = recorded_messages["official_all_liquidation_roseusdt"]
    events = connector.parse_all_liquidation(msg, incomplete=connector.has_disconnection_gap)
    assert events[0].incomplete is False

    # Corte registrado: incomplete pasa a True tanto en parser como en handle_raw_message
    connector.mark_disconnect()
    assert connector.has_disconnection_gap
    events_after_gap = connector.parse_all_liquidation(
        msg, incomplete=connector.has_disconnection_gap
    )
    assert events_after_gap[0].incomplete is True

    # handle_raw_message propaga automáticamente incomplete=True si hubo desconexión
    dispatched = await connector.handle_raw_message(json.dumps(msg))
    assert dispatched[0].incomplete is True
    queued = await connector.queue.get()
    assert queued.incomplete is True

    # Restablecer continuidad
    connector.reset_disconnect()
    assert not connector.has_disconnection_gap
    events_restored = connector.parse_all_liquidation(
        msg, incomplete=connector.has_disconnection_gap
    )
    assert events_restored[0].incomplete is False


def test_parse_malformed_messages(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica que mensajes con campos faltantes, tipos inválidos o tópicos erróneos sean descartados."""
    # Tópico no reconocido
    assert BybitConnector.parse_all_liquidation(recorded_messages["unrelated_topic"]) == []

    # Falta 'data' o no es lista
    assert BybitConnector.parse_all_liquidation({"topic": "allLiquidation.BTCUSDT"}) == []
    assert (
        BybitConnector.parse_all_liquidation({"topic": "allLiquidation.BTCUSDT", "data": "no_list"})
        == []
    )

    # Items dentro de data con campos faltantes o inválidos
    assert BybitConnector.parse_all_liquidation(recorded_messages["malformed_missing_fields"]) == []
    assert BybitConnector.parse_all_liquidation(recorded_messages["malformed_invalid_price"]) == []

    # Item que no sea dict o con lado inválido
    payload = {
        "topic": "allLiquidation.BTCUSDT",
        "data": ["not_a_dict", {"s": "BTCUSDT", "S": "UNKNOWN", "v": "1", "p": "100"}],
    }
    assert BybitConnector.parse_all_liquidation(payload) == []


@pytest.mark.asyncio
async def test_controlled_queue_emission(recorded_messages: dict[str, dict[str, Any]]) -> None:
    """Verifica que handle_raw_message despache la liquidación a la cola controlada y al handler."""
    custom_queue: asyncio.Queue[LiquidationEvent] = asyncio.Queue()
    connector = BybitConnector(symbol="ROSEUSDT", queue=custom_queue)

    received_handler: list[LiquidationEvent] = []

    async def on_liq(event: LiquidationEvent) -> None:
        received_handler.append(event)

    connector.register_liquidation_handler(on_liq)
    raw_json = json.dumps(recorded_messages["official_all_liquidation_roseusdt"])

    events = await connector.handle_raw_message(raw_json)
    assert len(events) == 1

    # Obtener el evento directamente de la cola controlada de manera determinista
    queued_event = await asyncio.wait_for(connector.queue.get(), timeout=1.0)
    assert queued_event.symbol == "ROSEUSDT"
    assert queued_event.bankruptcy_price == 0.04499
    assert queued_event.price is None
    assert queued_event.origin == DataOrigin.OBSERVED
    assert queued_event.coverage == DataCoverage.COMPLETE
    assert len(received_handler) == 1


@pytest.mark.asyncio
async def test_handle_raw_message_edge_cases() -> None:
    """Verifica manejo de errores de JSON y mensajes operativos."""
    connector = BybitConnector(symbol="BTCUSDT")

    # JSON inválido
    assert await connector.handle_raw_message("invalid json") == []

    # JSON que no es un objeto
    assert await connector.handle_raw_message(json.dumps([1, 2, 3])) == []

    # Mensaje operativo (subscribe / pong)
    assert await connector.handle_raw_message(json.dumps({"op": "pong"})) == []

    # Mensaje sin op ni topic de allLiquidation
    assert await connector.handle_raw_message(json.dumps({"unhandled": "data"})) == []


@pytest.mark.asyncio
async def test_start_and_stop_lifecycle() -> None:
    """Verifica el ciclo de vida de conexión y detención limpia del conector."""
    connector = BybitConnector(symbol="BTCUSDT")
    assert connector.status == ConnectionStatus.DISCONNECTED
    assert not connector.is_connected

    # Iniciar y comprobar que crea la tarea
    await connector.start()
    assert connector._running
    assert connector._task is not None

    # Llamar a start de nuevo no crea nueva tarea
    task1 = connector._task
    await connector.start()
    assert connector._task is task1

    # Detener de forma limpia
    await connector.stop()
    assert not connector._running
    assert connector._task is None
    assert connector.status == ConnectionStatus.DISCONNECTED

    # Detener cuando no hay tareas activas ni ws
    await connector.stop()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_loop_with_controlled_queue_and_mocked_ws(
    recorded_messages: dict[str, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Simula una sesión WebSocket activa sincronizada mediante la cola controlada sin sleeps arbitrarios."""
    connector = BybitConnector(symbol="ROSEUSDT")

    mock_msg = MagicMock()
    mock_msg.type = aiohttp.WSMsgType.TEXT
    mock_msg.data = json.dumps(recorded_messages["official_all_liquidation_roseusdt"])

    mock_close_msg = MagicMock()
    mock_close_msg.type = aiohttp.WSMsgType.CLOSED

    class AsyncIterator:
        def __init__(self, items: list[Any]) -> None:
            self.items = items

        def __aiter__(self) -> "AsyncIterator":
            return self

        async def __anext__(self) -> Any:
            if not self.items:
                raise StopAsyncIteration
            return self.items.pop(0)

    mock_ws = MagicMock()
    mock_ws.send_str = AsyncMock()
    mock_ws.close = AsyncMock()
    mock_ws.closed = False
    mock_ws.__aiter__ = lambda self: AsyncIterator([mock_msg, mock_close_msg])

    mock_session = MagicMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()

    class MockWsContext:
        async def __aenter__(self) -> MagicMock:
            return mock_ws

        async def __aexit__(self, *args: Any) -> None:
            pass

    mock_session.ws_connect = MagicMock(return_value=MockWsContext())

    class MockSessionContext:
        async def __aenter__(self) -> MagicMock:
            return mock_session

        async def __aexit__(self, *args: Any) -> None:
            pass

    monkeypatch.setattr(aiohttp, "ClientSession", lambda: MockSessionContext())

    await connector.start()

    # Sincronización exacta: esperar elemento en la cola controlada
    event = await asyncio.wait_for(connector.queue.get(), timeout=2.0)
    await connector.stop()

    assert event.symbol == "ROSEUSDT"
    assert event.bankruptcy_price == 0.04499
    assert event.price is None
    assert event.origin == DataOrigin.OBSERVED
    assert event.coverage == DataCoverage.COMPLETE


@pytest.mark.asyncio
async def test_connection_loop_unhandled_msg_type_and_stop_during_iter(
    recorded_messages: dict[str, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica que mensajes no manejados (PING) no rompan el bucle y que la cola reciba el mensaje posterior."""
    connector = BybitConnector(symbol="BTCUSDT")

    class MockPingWS:
        def __init__(self) -> None:
            self.closed = False

        async def send_str(self, data: str) -> None:
            pass

        async def close(self) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                yield MagicMock(type=aiohttp.WSMsgType.PING, data=b"")
                # Enviar mensaje válido con evento para sincronización
                yield MagicMock(
                    type=aiohttp.WSMsgType.TEXT,
                    data=json.dumps(recorded_messages["synthetic_all_liquidation_btcusdt"]),
                )
                yield MagicMock(type=aiohttp.WSMsgType.CLOSED)

            return gen()

    class MockPingWSContext:
        def __init__(self) -> None:
            self.ws = MockPingWS()

        async def __aenter__(self) -> MockPingWS:
            return self.ws

        async def __aexit__(self, *args: Any) -> None:
            self.ws.closed = True

    class MockClientSession:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "MockClientSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            self.closed = True

        async def close(self) -> None:
            self.closed = True

        def ws_connect(self, *args: Any, **kwargs: Any) -> MockPingWSContext:
            return MockPingWSContext()

    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: MockClientSession())

    await connector.start()
    event = await asyncio.wait_for(connector.queue.get(), timeout=2.0)
    await connector.stop()

    assert event.symbol == "BTCUSDT"
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_loop_exception_and_reconnect(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica manejo de excepciones de red utilizando una instancia de Settings aislada."""
    # Instancia aislada de Settings: nunca se modifica get_settings()
    custom_settings = Settings(
        ws_reconnect_min_delay_sec=0.01,
        ws_reconnect_jitter=0.0,
    )
    connector = BybitConnector(symbol="BTCUSDT", settings=custom_settings)

    reconnect_event = asyncio.Event()
    call_count = 0

    class FailingSession:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "FailingSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            self.closed = True

        async def close(self) -> None:
            self.closed = True

        def ws_connect(self, *args: Any, **kwargs: Any) -> Any:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionResetError("Conexión perdida")
            reconnect_event.set()
            raise asyncio.CancelledError()

    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: FailingSession())

    await connector.start()
    # Espera controlada por evento sin sleeps arbitrarios
    await asyncio.wait_for(reconnect_event.wait(), timeout=2.0)
    await connector.stop()

    assert call_count >= 2
    assert connector.has_disconnection_gap


@pytest.mark.asyncio
async def test_connection_loop_cancelled_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica manejo de CancelledError dentro del bloque try principal sincronizado con Event."""
    connector = BybitConnector(symbol="BTCUSDT")
    started_event = asyncio.Event()

    class CancelledSession:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "CancelledSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            self.closed = True

        async def close(self) -> None:
            self.closed = True

        def ws_connect(self, *args: Any, **kwargs: Any) -> Any:
            started_event.set()
            raise asyncio.CancelledError()

    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: CancelledSession())

    await connector.start()
    await asyncio.wait_for(started_event.wait(), timeout=2.0)
    await connector.stop()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_loop_reconnect_sleep_cancelled(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica interrupción limpia de la espera de reconexión al detener."""
    custom_settings = Settings(
        ws_reconnect_min_delay_sec=10.0,
        ws_reconnect_jitter=0.0,
    )
    connector = BybitConnector(symbol="BTCUSDT", settings=custom_settings)
    error_event = asyncio.Event()

    class ErrorSession:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "ErrorSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            self.closed = True

        async def close(self) -> None:
            self.closed = True

        def ws_connect(self, *args: Any, **kwargs: Any) -> Any:
            error_event.set()
            raise ConnectionError("network drop")

    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: ErrorSession())

    await connector.start()
    await asyncio.wait_for(error_event.wait(), timeout=2.0)
    # Detener mientras espera en reconnect sleep
    await connector.stop()
    assert connector.status == ConnectionStatus.DISCONNECTED
    assert connector.has_disconnection_gap


@pytest.mark.asyncio
async def test_connection_loop_not_running_initially() -> None:
    """Verifica que _connection_loop sale inmediatamente si _running es False (222->278)."""
    connector = BybitConnector(symbol="BTCUSDT")
    assert not connector._running
    await connector._connection_loop()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_loop_stopped_during_ws_iteration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verifica salida inmediata (líneas 246 y 263) cuando _running pasa a False durante la iteración."""
    connector = BybitConnector(symbol="BTCUSDT")

    class MockIterWS:
        def __init__(self) -> None:
            self.closed = False

        async def send_str(self, data: str) -> None:
            pass

        async def close(self) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                # Primer mensaje: cambia _running a False para forzar la condición en el siguiente ciclo
                connector._running = False
                yield MagicMock(type=aiohttp.WSMsgType.PING, data=b"")
                # Segundo mensaje: el loop de ws encuentra `if not self._running:` y ejecuta `break` (línea 246)
                yield MagicMock(type=aiohttp.WSMsgType.TEXT, data="{}")

            return gen()

    class MockIterSession:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "MockIterSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            self.closed = True

        async def close(self) -> None:
            self.closed = True

        def ws_connect(self, *args: Any, **kwargs: Any) -> Any:
            class Context:
                async def __aenter__(self) -> MockIterWS:
                    return MockIterWS()

                async def __aexit__(self, *args: Any) -> None:
                    pass

            return Context()

    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: MockIterSession())

    connector._running = True
    await connector._connection_loop()
    assert connector.status == ConnectionStatus.DISCONNECTED


@pytest.mark.asyncio
async def test_connection_loop_ws_iteration_natural_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifica rama 244->262 cuando el websocket finaliza la iteración normalmente."""
    custom_settings = Settings(
        ws_reconnect_min_delay_sec=10.0,
        ws_reconnect_jitter=0.0,
    )
    connector = BybitConnector(symbol="BTCUSDT", settings=custom_settings)
    exhausted_event = asyncio.Event()

    class MockExhaustWS:
        def __init__(self) -> None:
            self.closed = False

        async def send_str(self, data: str) -> None:
            pass

        async def close(self) -> None:
            self.closed = True

        def __aiter__(self) -> Any:
            async def gen() -> Any:
                # Generador que termina naturalmente sin yield ni break por closed/error
                exhausted_event.set()
                if False:
                    yield None

            return gen()

    class MockExhaustSession:
        def __init__(self) -> None:
            self.closed = False

        async def __aenter__(self) -> "MockExhaustSession":
            return self

        async def __aexit__(self, *args: Any) -> None:
            self.closed = True

        async def close(self) -> None:
            self.closed = True

        def ws_connect(self, *args: Any, **kwargs: Any) -> Any:
            class Context:
                async def __aenter__(self) -> MockExhaustWS:
                    return MockExhaustWS()

                async def __aexit__(self, *args: Any) -> None:
                    pass

            return Context()

    monkeypatch.setattr(aiohttp, "ClientSession", lambda **kwargs: MockExhaustSession())

    await connector.start()
    await asyncio.wait_for(exhausted_event.wait(), timeout=2.0)
    # Tras agotar el generador, pasa por 262 y entra en estado RECONNECTING
    await connector.stop()
    assert connector.has_disconnection_gap
