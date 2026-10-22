# Supuestos del Modelo Matemático y Fuentes — LiqScope

> [!IMPORTANT]
> Todo dato calculado o presentado en el mapa de calor de LiqScope es una **ESTIMACIÓN** analítica con fines informativos. No representa una orden garantizada ni asesoramiento financiero.

---

## 1. Clasificación del Origen de Datos (`DataOrigin`)

El modelo diferencia estrictamente entre dos naturalezas de datos según el exchange emisor:

1. **Datos Reales (`REAL`):**
   - **Fuente:** Hyperliquid L1/L2 On-Chain Info API (`https://api.hyperliquid.xyz/info`).
   - **Fundamento:** Al ser un exchange perpetuo descentralizado con libro de órdenes on-chain y liquidación programática, el estado del margen, apalancamiento exacto, tamaño y precio de liquidación de las cuentas es público y verificable en el estado del clearinghouse.
2. **Datos Estimados (`ESTIMATED`):**
   - **Fuentes:** Binance Futures USDT-M y Bybit Linear.
   - **Fundamento:** Los CEX centralizados no publican los libros de posiciones individuales abiertas por motivos de privacidad comercial. Publican el Open Interest global, el flujo de operaciones (trades) y los eventos forzados de liquidación ejecutados (`forceOrder`).
   - **Limitación Oficial de `forceOrder` en Binance:** Según la documentación oficial de [Binance Liquidation Order Streams](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams), el stream se actualiza cada **1000 ms** y entrega únicamente la liquidación **más grande** ocurrida en dicho segundo por símbolo. En consecuencia, el volumen público de `forceOrder` representa un muestreo conservador (límite inferior) del volumen total liquidado en Binance, no el 100 % absoluto. Por tanto, la masa de posiciones vivas por rango de precio se aproxima estadísticamente mediante el modelo del motor.

---

## 2. Supuestos de Distribución de Apalancamientos en CEX

En ausencia de datos de posiciones individuales en CEX, el motor de LiqScope distribuye el Open Interest incremental a través de un conjunto de escalones de apalancamiento típicos ponderados:

| Apalancamiento ($L$) | Peso por Defecto | Justificación de Mercado |
|---|---|---|
| **5x** | 0.15 | Operativa institucional / swing trading conservador |
| **10x** | 0.25 | Apalancamiento estándar común en traders con gestión de riesgo |
| **25x** | 0.30 | Nivel más popular para retail activo en CEX principales |
| **50x** | 0.20 | Especulación intradía de alta volatilidad |
| **100x** | 0.10 | Máximo apalancamiento retail frecuente |

Estos parámetros se configuran externamente en `config/default_distribution.yaml` y son mostrados explícitamente en la interfaz de usuario para total transparencia analítica.

---

## 3. Fórmulas de Precio de Liquidación

### 3.1. Margen Aislado Lineal (Aproximación inicial)
Para contratos lineales cotizados en USDT/USDC con precio de entrada $P_{\text{entry}}$, apalancamiento $L$ y tasa de margen de mantenimiento $\text{MMR}$:

- **Posición Larga (Long):**
  $$P_{\text{liq, long}} \approx P_{\text{entry}} \times \left(1 - \frac{1}{L} + \text{MMR}\right)$$
- **Posición Corta (Short):**
  $$P_{\text{liq, short}} \approx P_{\text{entry}} \times \left(1 + \frac{1}{L} - \text{MMR}\right)$$

### 3.2. Fuentes Oficiales de Escalones de Mantenimiento (Tiers)
- **Binance Futures:** [Binance Leverage and Margin of USDⓈ-M Futures](https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin)
- **Bybit Linear:** [Bybit Margin & Risk Limit (USDT Perpetual)](https://www.bybit.com/en/help-center/article/Risk-Limit-USDT-Perpetual)
- **Hyperliquid:** [Hyperliquid Documentation - Margin Requirements](https://hyperliquid.gitbook.io/hyperliquid-docs)

---

## 4. Fixtures de Demostración Sintéticos

Para soportar el **Modo Demo / Offline** y tests automatizados sin requerir conectividad de red ni credenciales:
- Todos los archivos en el directorio `fixtures/demo/` contienen datos **100 % sintéticos**.
- Cada archivo incluye en su raíz los campos `_synthetic: true` y `_notice` advirtiendo explícitamente su naturaleza ficticia.
- No representan cuentas reales, saldos de usuarios ni libros de órdenes en vivo.
