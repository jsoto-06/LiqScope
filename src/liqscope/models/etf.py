"""Modelos Pydantic para el Tracker Institucional de ETFs Spot (Bitcoin & Ethereum)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ETFItem(BaseModel):
    """Métricas individuales de un fondo cotizado (ETF) spot."""

    ticker: str = Field(description="Ticker del ETF (ej. IBIT, FBTC)")
    issuer: str = Field(description="Entidad gestora / emisor (ej. BlackRock, Fidelity)")
    name: str = Field(description="Nombre completo del fondo")
    aum_usd: float = Field(description="Activos bajo gestión en USD (AUM)")
    crypto_holdings: float = Field(description="Criptomonedas en custodia física (BTC o ETH)")
    net_inflow_today_usd: float = Field(description="Flujo neto en la última sesión en USD")
    cumulative_inflow_usd: float = Field(description="Flujo neto acumulado histórico en USD")
    fee_pct: float = Field(description="Comisión de gestión anual (Expense Ratio %)")
    custodian: str = Field(description="Custodio institucional (ej. Coinbase Prime)")


class DailyInflowRecord(BaseModel):
    """Registro de flujo neto diario institucional."""

    date: str = Field(description="Fecha de la sesión de mercado (YYYY-MM-DD)")
    net_inflow_usd: float = Field(description="Flujo neto consolidado del día en USD")
    crypto_equivalent: float = Field(description="Equivalente en BTC o ETH absorbido o liquidado")
    top_inflow_ticker: str = Field(description="Fondo con mayor volumen de entrada neta")


class ETFSnapshot(BaseModel):
    """Instantánea institucional consolidada para una criptomoneda (BTC o ETH)."""

    asset: str = Field(description="Activo subyacente: BTC o ETH")
    total_aum_usd: float = Field(description="AUM total agregado de todos los fondos en USD")
    total_crypto_holdings: float = Field(description="Total de monedas en reserva en custodia")
    net_inflow_today_usd: float = Field(description="Flujo neto agregado en la última sesión (USD)")
    cumulative_inflow_usd: float = Field(description="Flujo neto agregado acumulado histórico (USD)")
    dominant_fund: str = Field(description="Fondo con mayor cuota de mercado")
    funds: list[ETFItem] = Field(description="Desglose por fondo emisor")
    daily_history: list[DailyInflowRecord] = Field(description="Historial diario de flujos netos")


class ETFTrackerResponse(BaseModel):
    """Respuesta completa del Tracker Institucional de ETFs."""

    btc_etf: ETFSnapshot
    eth_etf: ETFSnapshot
    timestamp: int = Field(description="Unix timestamp de actualización")
    institutional_sentiment: str = Field(
        description="Evaluación del flujo institucional: AGGRESSIVE_INFLOW, MODERATE_INFLOW, OUTFLOW, NEUTRAL"
    )
