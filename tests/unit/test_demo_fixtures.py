"""Tests unitarios para los fixtures sintéticos del modo demo."""

import json
from pathlib import Path

import pytest

from liqscope.demo.loader import DemoDataLoader


def test_demo_fixtures_contain_synthetic_flag(demo_loader: DemoDataLoader) -> None:
    """Verifica que todos los fixtures de demo contengan el flag obligatorio '_synthetic: true'."""
    fixture_files = [
        "binance_trades.json",
        "binance_force_orders.json",
        "binance_open_interest.json",
        "hyperliquid_positions.json",
    ]

    for fname in fixture_files:
        payload = demo_loader.load_fixture(fname)
        assert payload.get("_synthetic") is True, f"{fname} no contiene '_synthetic: true'"
        assert "_notice" in payload, f"{fname} no contiene advertencia '_notice'"
        assert "SYNTHETIC DEMO DATA" in payload["_notice"]


def test_demo_loader_methods(demo_loader: DemoDataLoader) -> None:
    """Verifica los métodos de carga individuales del cargador de demo."""
    trades = demo_loader.get_binance_trades()
    assert isinstance(trades, list)
    assert len(trades) > 0
    assert trades[0]["e"] == "aggTrade"

    force_orders = demo_loader.get_binance_force_orders()
    assert isinstance(force_orders, list)
    assert len(force_orders) > 0
    assert force_orders[0]["e"] == "forceOrder"

    oi = demo_loader.get_binance_open_interest()
    assert isinstance(oi, dict)
    assert "openInterest" in oi
    assert oi["symbol"] == "BTCUSDT"

    positions = demo_loader.get_hyperliquid_positions()
    assert isinstance(positions, list)
    assert len(positions) > 0
    assert "position" in positions[0]


def test_loader_rejects_missing_synthetic_flag(tmp_path: Path) -> None:
    """Verifica que el cargador rechace explícitamente cualquier fixture no marcado como sintético."""
    bad_fixture = tmp_path / "unsafe_fixture.json"
    with open(bad_fixture, "w", encoding="utf-8") as f:
        json.dump({"data": [1, 2, 3]}, f)

    loader = DemoDataLoader(fixtures_dir=tmp_path)
    with pytest.raises(ValueError) as exc_info:
        loader.load_fixture("unsafe_fixture.json")
    assert "no tiene el flag '_synthetic: true'" in str(exc_info.value)


def test_loader_nonexistent_file_raises_not_found(demo_loader: DemoDataLoader) -> None:
    """Verifica que se lance FileNotFoundError ante archivos inexistentes."""
    with pytest.raises(FileNotFoundError):
        demo_loader.load_fixture("non_existent_fixture.json")


def test_loader_rejects_non_dict_json(tmp_path: Path) -> None:
    """Verifica que el cargador rechace fixtures cuyo contenido raíz no sea un objeto JSON."""
    bad_fixture = tmp_path / "list_root.json"
    with open(bad_fixture, "w", encoding="utf-8") as f:
        json.dump(["item1", "item2"], f)

    loader = DemoDataLoader(fixtures_dir=tmp_path)
    with pytest.raises(ValueError) as exc_info:
        loader.load_fixture("list_root.json")
    assert "se esperaba un objeto JSON" in str(exc_info.value)


def test_loader_validates_data_field_types(tmp_path: Path) -> None:
    """Verifica que se valide el tipo del campo 'data' en cada método específico."""
    bad_fixture = tmp_path / "binance_trades.json"
    with open(bad_fixture, "w", encoding="utf-8") as f:
        json.dump({"_synthetic": True, "data": "not-a-list"}, f)

    bad_fo = tmp_path / "binance_force_orders.json"
    with open(bad_fo, "w", encoding="utf-8") as f:
        json.dump({"_synthetic": True, "data": "not-a-list"}, f)

    bad_oi = tmp_path / "binance_open_interest.json"
    with open(bad_oi, "w", encoding="utf-8") as f:
        json.dump({"_synthetic": True, "data": ["should-be-dict"]}, f)

    bad_pos = tmp_path / "hyperliquid_positions.json"
    with open(bad_pos, "w", encoding="utf-8") as f:
        json.dump({"_synthetic": True, "data": "not-a-list"}, f)

    loader = DemoDataLoader(fixtures_dir=tmp_path)
    with pytest.raises(ValueError) as exc_info:
        loader.get_binance_trades()
    assert "debe ser una lista de trades" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        loader.get_binance_force_orders()
    assert "debe ser una lista de force orders" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        loader.get_binance_open_interest()
    assert "debe ser un objeto de open interest" in str(exc_info.value)

    with pytest.raises(ValueError) as exc_info:
        loader.get_hyperliquid_positions()
    assert "debe ser una lista de posiciones" in str(exc_info.value)
