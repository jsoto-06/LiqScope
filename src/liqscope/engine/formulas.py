"""Fórmulas matemáticas para estimación de precios de liquidación apalancada.

Fórmulas implementadas:
1. Margen Aislado Lineal (Aproximación inicial):
   - LONG:  precio_liq ≈ entrada * (1 - 1/apalancamiento + MMR)
   - SHORT: precio_liq ≈ entrada * (1 + 1/apalancamiento - MMR)
2. Margen Aislado Exacto (con escalones y deducción acumulada de tiers):
   - LONG:  precio_liq = (entrada * (1 - 1/L) + cum / Q) / (1 - MMR)
   - SHORT: precio_liq = (entrada * (1 + 1/L) - cum / Q) / (1 + MMR)

Documentación Oficial:
https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin
"""

from liqscope.models.common import PositionSide


def calculate_approximate_liquidation_price(
    entry_price: float,
    leverage: float,
    side: PositionSide,
    maintenance_margin_rate: float,
) -> float:
    """Calcula el precio de liquidación aproximado para contratos lineales con margen aislado.

    Fórmula:
      LONG:  entrada * (1 - 1/leverage + MMR)
      SHORT: entrada * (1 + 1/leverage - MMR)

    Args:
        entry_price: Precio medio de entrada de la posición (>0).
        leverage: Nivel de apalancamiento (>=1.0).
        side: Dirección de la posición (PositionSide.LONG o PositionSide.SHORT).
        maintenance_margin_rate: Tasa MMR decimal supuesta o verificada (ej. 0.004 para 0.4%).

    Returns:
        Precio de liquidación estimado redondeado a 4 decimales.
    """
    if entry_price <= 0:
        raise ValueError(f"El precio de entrada debe ser positivo (>0), recibido: {entry_price}")
    if leverage < 1.0:
        raise ValueError(f"El apalancamiento debe ser >= 1.0, recibido: {leverage}")
    if maintenance_margin_rate < 0:
        raise ValueError(f"El MMR debe ser mayor o igual a 0, recibido: {maintenance_margin_rate}")

    inv_leverage = 1.0 / leverage

    if side == PositionSide.LONG:
        factor = 1.0 - inv_leverage + maintenance_margin_rate
        liq_price = entry_price * factor
        # Una liquidación long no puede ser negativa
        return max(0.0, round(liq_price, 4))

    if side == PositionSide.SHORT:
        factor = 1.0 + inv_leverage - maintenance_margin_rate
        liq_price = entry_price * factor
        return round(liq_price, 4)

    raise ValueError(f"Dirección de posición no soportada para liquidación: {side}")


def calculate_exact_tier_liquidation_price(
    entry_price: float,
    leverage: float,
    side: PositionSide,
    maintenance_margin_rate: float,
    cum_maintenance_amount: float = 0.0,
    quantity: float = 1.0,
) -> float:
    """Calcula el precio de liquidación exacto con tiers de margen de mantenimiento oficial.

    Args:
        entry_price: Precio de entrada.
        leverage: Apalancamiento.
        side: Lado de la posición (LONG o SHORT).
        maintenance_margin_rate: Tasa de margen de mantenimiento del tier.
        cum_maintenance_amount: Deducción acumulada del tier en USD.
        quantity: Tamaño de la posición en contratos / unidades base.
    """
    if entry_price <= 0 or leverage < 1.0 or quantity <= 0:
        raise ValueError("Parámetros numéricos inválidos para cálculo exacto")

    inv_leverage = 1.0 / leverage
    cum_per_qty = cum_maintenance_amount / quantity

    if side == PositionSide.LONG:
        numerator = entry_price * (1.0 - inv_leverage) + cum_per_qty
        denominator = 1.0 - maintenance_margin_rate
        if denominator <= 0:
            raise ValueError("Denominador inválido en cálculo de liquidación")
        return max(0.0, round(numerator / denominator, 4))

    if side == PositionSide.SHORT:
        numerator = entry_price * (1.0 + inv_leverage) - cum_per_qty
        denominator = 1.0 + maintenance_margin_rate
        return round(numerator / denominator, 4)

    raise ValueError(f"Dirección no soportada: {side}")
