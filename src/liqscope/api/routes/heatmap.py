"""Rutas de la API para la visualización del mapa de calor de liquidaciones estimadas."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse

from liqscope.config import Settings
from liqscope.connectors.binance_rest import (
    SUPPORTED_SYMBOLS,
    BinanceFuturesRestClient,
    BinanceMarketData,
    BinanceRateLimitError,
    BinanceRestError,
    UnsupportedSymbolError,
)
from liqscope.engine.aggregator import build_heatmap_snapshot
from liqscope.models.heatmap import HeatmapSnapshot

router = APIRouter(prefix="/heatmap", tags=["Heatmap"])


def get_settings() -> Settings:
    """Proveedor de dependencias para la configuración de LiqScope."""
    return Settings()


async def get_binance_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[BinanceFuturesRestClient, None]:
    """Generador de contexto asíncrono para el cliente REST de Binance."""
    async with BinanceFuturesRestClient(
        base_url=settings.binance_rest_url,
        timeout_sec=settings.http_request_timeout_sec,
    ) as client:
        yield client


@router.get(
    "/{symbol}",
    response_model=HeatmapSnapshot,
    summary="Mapa de calor de liquidaciones estimadas",
    description="Retorna el snapshot modelado de zonas de liquidación para BTCUSDT o ETHUSDT.",
    responses={
        200: {"description": "Instantánea de mapa de calor calculada exitosamente."},
        400: {"description": "Símbolo no soportado o parámetros de rango inválidos."},
        429: {"description": "Límite de peticiones de Binance alcanzado (Rate Limit)."},
        418: {"description": "Dirección IP bloqueada por límite de tasa de Binance."},
        502: {"description": "Error al comunicar con la API de Binance."},
        503: {"description": "Servicio de Binance o red no disponible."},
        504: {"description": "Timeout al conectar con la API de Binance."},
    },
)
async def get_heatmap(
    symbol: str,
    min_price: float | None = Query(
        default=None,
        description="Límite inferior del rango de precio a visualizar (USD)",
    ),
    max_price: float | None = Query(
        default=None,
        description="Límite superior del rango de precio a visualizar (USD)",
    ),
    bin_size: float = Query(
        default=50.0,
        gt=0,
        description="Tamaño discreto de cada celda/bin en USD",
    ),
    assumed_long_ratio: float = Query(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Ratio supuesto de volumen en posiciones long (0.0 a 1.0)",
    ),
    source: str = Query(
        default="live",
        description="Origen de los datos: 'live' (Binance en vivo) o 'demo' (sintético)",
    ),
    client: BinanceFuturesRestClient = Depends(get_binance_client),
) -> Response | HeatmapSnapshot:
    """Endpoint principal de consulta del Heatmap de liquidaciones."""
    normalized_sym = symbol.upper().strip()
    if normalized_sym not in SUPPORTED_SYMBOLS:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": (
                    f"Símbolo no soportado en esta fase: '{symbol}'. "
                    f"Solo se admiten: {', '.join(sorted(SUPPORTED_SYMBOLS))}."
                ),
                "status_code": 400,
                "source": source,
            },
        )

    if min_price is not None and max_price is not None and min_price > max_price:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": f"min_price ({min_price}) no puede ser mayor que max_price ({max_price}).",
                "status_code": 400,
                "source": source,
            },
        )

    # 1. Obtención de datos de mercado (demo o live)
    if source.lower() == "demo":
        # Datos sintéticos de demostración
        demo_mark_price = 81498.90 if normalized_sym == "BTCUSDT" else 2650.50
        demo_oi = 95448.751 if normalized_sym == "BTCUSDT" else 350000.0
        market_data = BinanceMarketData(
            symbol=normalized_sym,
            mark_price=demo_mark_price,
            open_interest=demo_oi,
            open_interest_time=1729630000000,
            premium_index_time=1729630000000,
            source="demo",
        )
    else:
        try:
            market_data = await client.get_market_data(normalized_sym)
        except BinanceRateLimitError as e:
            headers: dict[str, str] = {}
            if e.retry_after is not None:
                headers["Retry-After"] = str(e.retry_after)
            err_dict = e.to_dict()
            err_dict["source"] = source
            rate_status = (
                e.status_code if e.status_code is not None else status.HTTP_429_TOO_MANY_REQUESTS
            )
            return JSONResponse(
                status_code=rate_status,
                content=err_dict,
                headers=headers,
            )
        except (BinanceRestError, UnsupportedSymbolError) as e:
            err_dict = e.to_dict()
            err_dict["source"] = source
            status_code = (
                e.status_code if e.status_code is not None else status.HTTP_502_BAD_GATEWAY
            )
            return JSONResponse(
                status_code=status_code,
                content=err_dict,
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": f"Error inesperado al obtener datos de mercado: {e}",
                    "status_code": 500,
                    "source": source,
                },
            )

    # 2. Modelado y agregación del snapshot de liquidaciones
    total_oi_usd = market_data.open_interest * market_data.mark_price

    return build_heatmap_snapshot(
        symbol=market_data.symbol,
        mark_price=market_data.mark_price,
        total_open_interest_usd=total_oi_usd,
        bin_size=bin_size,
        min_price=min_price,
        max_price=max_price,
        assumed_long_ratio=assumed_long_ratio,
        source=market_data.source,
    )
