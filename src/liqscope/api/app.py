"""Inicialización de la aplicación FastAPI para LiqScope."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from liqscope.api.routes.heatmap import router as heatmap_router
from liqscope.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """Fábrica de inicialización y configuración de la aplicación FastAPI."""
    cfg = settings or Settings()

    app = FastAPI(
        title="LiqScope API",
        version="0.1.0",
        description="Visualización y modelado analítico de zonas de liquidación para derivados cripto.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware CORS
    if cfg.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cfg.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Inclusión de routers
    app.include_router(heatmap_router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        """Endpoint de salud del servicio."""
        return {"status": "ok", "env": cfg.env.value}

    return app
