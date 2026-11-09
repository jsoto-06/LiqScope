"""Rutas y módulos de endpoints de LiqScope."""

from liqscope.api.routes.alerts import router as alerts_router
from liqscope.api.routes.etf import router as etf_router
from liqscope.api.routes.funding import router as funding_router
from liqscope.api.routes.heatmap import router as heatmap_router
from liqscope.api.routes.klines import router as klines_router
from liqscope.api.routes.liquidations import router as liquidations_router
from liqscope.api.routes.screener import router as screener_router
from liqscope.api.routes.symbols import router as symbols_router

__all__ = [
    "alerts_router",
    "etf_router",
    "funding_router",
    "heatmap_router",
    "klines_router",
    "liquidations_router",
    "screener_router",
    "symbols_router",
]
