"""Inicialización de la aplicación FastAPI para LiqScope."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from liqscope.api.dashboard import get_dashboard_html
from liqscope.api.routes.alerts import router as alerts_router
from liqscope.api.routes.etf import router as etf_router
from liqscope.api.routes.funding import router as funding_router
from liqscope.api.routes.heatmap import router as heatmap_router
from liqscope.api.routes.klines import router as klines_router
from liqscope.api.routes.liquidations import router as liquidations_router, websocket_liquidation_stream
from liqscope.api.routes.screener import router as screener_router
from liqscope.api.routes.symbols import router as symbols_router
from liqscope.config import Settings
from liqscope.services.liquidation_feed import get_liquidation_feed_service
from liqscope.services.telegram_bot import TelegramBotService


def create_app(settings: Settings | None = None) -> FastAPI:
    """Fábrica de inicialización y configuración de la aplicación FastAPI."""
    cfg = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Ciclo de vida de la aplicación con feed de liquidaciones y bot interactivo."""
        bot_service: TelegramBotService | None = None
        feed_service = None

        if cfg.env.value != "test":
            feed_service = get_liquidation_feed_service()
            feed_service.start()

            if cfg.telegram_bot_token.strip():
                bot_service = TelegramBotService(settings=cfg)
                bot_service.start()

        try:
            yield
        finally:
            if bot_service:
                await bot_service.stop()
            if feed_service:
                await feed_service.stop()

    app = FastAPI(
        title="LiqScope API",
        version="0.1.0",
        description="Visualización y modelado analítico de zonas de liquidación para derivados cripto.",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware CORS
    if cfg.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cfg.cors_origins,
            allow_credentials=cfg.cors_allow_credentials,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Inclusión de routers canónicos versionados (/api/v1)
    app.include_router(heatmap_router, prefix="/api/v1")
    app.include_router(symbols_router, prefix="/api/v1")
    app.include_router(alerts_router, prefix="/api/v1")
    app.include_router(liquidations_router, prefix="/api/v1")
    app.include_router(klines_router, prefix="/api/v1")
    app.include_router(funding_router, prefix="/api/v1")
    app.include_router(screener_router, prefix="/api/v1")
    app.include_router(etf_router, prefix="/api/v1")

    # Alias canónico de WebSocket directo
    app.add_api_websocket_route("/ws/liquidations", websocket_liquidation_stream)

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def index() -> HTMLResponse:
        """Dashboard interactivo visual del Heatmap."""
        return HTMLResponse(content=get_dashboard_html(), status_code=200)

    @app.get("/manual", response_class=HTMLResponse, include_in_schema=False)
    async def manual() -> HTMLResponse:
        """Manual de usuario detallado y guía de telemetría."""
        return HTMLResponse(content=get_dashboard_html(), status_code=200)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Endpoint de salud del servicio."""
        return {"status": "ok", "env": cfg.env.value}

    return app
