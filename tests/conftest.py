"""Configuración global de tests para LiqScope."""

from pathlib import Path

import pytest

from liqscope.config import Settings
from liqscope.demo.loader import DemoDataLoader
from liqscope.models.common import Environment


@pytest.fixture
def test_settings() -> Settings:
    """Fixture que proporciona una configuración aislada para tests."""
    return Settings(
        env=Environment.TEST,
        host="127.0.0.1",
        port=8080,
        ws_reconnect_min_delay_sec=0.1,
        ws_reconnect_max_delay_sec=1.0,
        ws_reconnect_jitter=0.1,
        http_request_timeout_sec=2.0,
        stale_data_threshold_sec=5.0,
    )


@pytest.fixture
def demo_loader(tmp_path: Path) -> DemoDataLoader:
    """Fixture con el cargador apuntando a los fixtures del proyecto."""
    fixtures_path = Path(__file__).parent.parent / "fixtures" / "demo"
    return DemoDataLoader(fixtures_dir=fixtures_path)
