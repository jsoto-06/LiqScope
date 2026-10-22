"""Cargador de fixtures de demostración sintéticos para modo offline y testing."""

import json
from pathlib import Path
from typing import Any


class DemoDataLoader:
    """Cargador seguro de datasets sintéticos locales."""

    def __init__(self, fixtures_dir: Path | str = "fixtures/demo") -> None:
        self.fixtures_dir = Path(fixtures_dir)

    def load_fixture(self, filename: str) -> dict[str, Any]:
        """Carga un archivo fixture y valida que esté marcado explícitamente como sintético."""
        file_path = self.fixtures_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Fixture no encontrado: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Formato inválido en {filename}: se esperaba un objeto JSON")

        if not data.get("_synthetic", False):
            raise ValueError(
                f"El fixture {filename} no tiene el flag '_synthetic: true'. "
                "Todos los datos de demo deben estar explícitamente marcados como sintéticos."
            )

        return data

    def get_binance_trades(self) -> list[dict[str, Any]]:
        """Retorna la lista de trades sintéticos de Binance."""
        payload = self.load_fixture("binance_trades.json")
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ValueError("El campo 'data' debe ser una lista de trades")
        return data

    def get_binance_force_orders(self) -> list[dict[str, Any]]:
        """Retorna la lista de eventos de liquidación forzada sintéticos de Binance."""
        payload = self.load_fixture("binance_force_orders.json")
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ValueError("El campo 'data' debe ser una lista de force orders")
        return data

    def get_binance_open_interest(self) -> dict[str, Any]:
        """Retorna el Open Interest sintético de Binance."""
        payload = self.load_fixture("binance_open_interest.json")
        data = payload.get("data", {})
        if not isinstance(data, dict):
            raise ValueError("El campo 'data' debe ser un objeto de open interest")
        return data

    def get_hyperliquid_positions(self) -> list[dict[str, Any]]:
        """Retorna las posiciones on-chain sintéticas de Hyperliquid."""
        payload = self.load_fixture("hyperliquid_positions.json")
        data = payload.get("data", [])
        if not isinstance(data, list):
            raise ValueError("El campo 'data' debe ser una lista de posiciones")
        return data
