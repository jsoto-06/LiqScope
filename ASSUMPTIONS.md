# Supuestos del Modelo Matemático y Fuentes — LiqScope

> [!IMPORTANT]
> Todo dato calculado o presentado en el mapa de calor de LiqScope es una **ESTIMACIÓN** analítica con fines informativos. No representa una orden garantizada ni asesoramiento financiero.

---

## 1. Clasificación del Origen de Datos (`DataOrigin`)

El modelo diferencia estrictamente entre dos naturalezas de datos según el exchange emisor:

1. **Datos Reales (`REAL`):**
   - **Fuente:** Hyperliquid L1/L2 On-Chain Info API (`https://api.hyperliquid.xyz/info`).
   - **Fundamento:** Al ser un exchange perpetuo descentralizado con libro de órdenes on-chain y liquidación programática, el estado del margen, apalancamiento exacto, tamaño y precio de liquidación de las cuentas es público y verificable en el estado del clearinghouse.
   - **Restricción y Supuesto Operativo de Hyperliquid:** La API oficial de Hyperliquid (`clearinghouseState`) **requiere consultar direcciones de billetera específicas** (`{"type": "clearinghouseState", "user": "0x..."}`) y no ofrece un volcado global anónimo de todas las posiciones abiertas del exchange en una sola llamada. Por lo tanto, el mapa de liquidaciones reales de Hyperliquid en LiqScope se basa en el seguimiento de un conjunto seleccionado de **direcciones conocidas** (traders líderes del leaderboard, bóvedas históricas o cuentas descubiertas mediante trades recientes) y representa la muestra verificable de dichas cuentas, no el universo absoluto no indexado.
2. **Datos Estimados (`ESTIMATED`):**
   - **Fuentes:** Binance Futures USDT-M y Bybit Linear.
   - **Fundamento:** Los CEX centralizados no publican los libros de posiciones individuales abiertas por motivos de privacidad comercial. Publican el Open Interest global, el flujo de operaciones (trades) y los eventos forzados de liquidación ejecutados (`forceOrder`).
   - **Limitación y Supuesto de `forceOrder` en Binance (NO VERIFICADA):** La cifra de frecuencia de **1000 ms** y la premisa de entrega de únicamente la liquidación más grande por segundo proceden de referencias habituales pero **carecen de cita literal verificable**, dado que la página web oficial de documentación (`developers.binance.com`) devuelve `HTTP 202` (desafío anti-bot Cloudflare). Por tanto, se etiqueta formalmente como **supuesto no verificado**. En consecuencia, el volumen público de `forceOrder` se trata operativamente como un muestreo conservador (límite inferior) del volumen total liquidado en Binance, no el 100 % absoluto, y la masa de posiciones vivas por rango de precio se aproxima estadísticamente mediante el motor.

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

### 3.2. Fuentes y Estado de Verificación de Escalones de Mantenimiento (Tiers)

- **Binance Futures USDⓈ-M:**
  - **URL:** [https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin](https://www.binance.com/en/futures/trading-rules/perpetual/leverage-margin)
  - **Fecha de Consulta:** `2026-10-22`
  - **Estado:** **`PENDING_VERIFICATION`** (La página web oficial de reglas de trading devuelve `HTTP 202 Accepted` con longitud 0 a clientes no interactivos por desafío anti-bot Cloudflare, por lo que no es posible extraer el texto literal mediante scripts).
  - **Retirada de tablas, Supuestos sin verificar y Verificación oficial:** Se retiran todas las tablas de tiers de la documentación y de los informes. Todos los escalones numéricos en `tiers.py` y en las pruebas se definen con `status="PENDING_VERIFICATION"` y son **supuestos analíticos sin verificar**, no datos oficiales confirmados. La verificación programática oficial de estos escalones requiere consultar el endpoint autenticado `GET /fapi/v1/leverageBracket` de Binance Futures, el cual exige una API key válida con permisos de lectura (endpoint de tipo `USER_DATA`). Al no contar ni requerir credenciales en esta fase de visualización analítica pública, los valores se mantienen estrictamente como supuestos en el código.
- **Bybit Linear:** [Bybit Margin & Risk Limit (USDT Perpetual)](https://www.bybit.com/en/help-center/article/Risk-Limit-USDT-Perpetual) — *(Diferido a Fase 3)*.
- **Hyperliquid:** [Hyperliquid Documentation - Margin Requirements](https://hyperliquid.gitbook.io/hyperliquid-docs) — *(Diferido a Fase 3)*.

### 3.3. Límites de Tasa (Rate Limits) de Binance Futures
- **Endpoint en vivo:** `https://fapi.binance.com/fapi/v1/exchangeInfo` (Consultado el `2026-10-22`).
- **Respuesta JSON de la API:**
  ```json
  [
    {"rateLimitType": "REQUEST_WEIGHT", "interval": "MINUTE", "intervalNum": 1, "limit": 2400},
    {"rateLimitType": "ORDERS", "interval": "MINUTE", "intervalNum": 1, "limit": 1200},
    {"rateLimitType": "ORDERS", "interval": "SECOND", "intervalNum": 10, "limit": 300}
  ]
  ```
- **Estado de la documentación en texto (`developers.binance.com`):** La página web devuelve `HTTP 202` (Cloudflare). Se retira cualquier mención a la frase *"A Retry-After header will be sent with a 418 or 429 response"* (perteneciente a Spot). El límite de 2.400 weight/min se toma con la evidencia JSON de la API viva, quedando la cita literal de texto de la página como **`PENDING_VERIFICATION`**.

---

## 4. Fixtures de Demostración Sintéticos

Para soportar el **Modo Demo / Offline** y tests automatizados sin requerir conectividad de red ni credenciales:
- Todos los archivos en el directorio `fixtures/demo/` contienen datos **100 % sintéticos**.
- Cada archivo incluye en su raíz los campos `_synthetic: true` y `_notice` advirtiendo explícitamente su naturaleza ficticia.
- No representan cuentas reales, saldos de usuarios ni libros de órdenes en vivo.


---

## 5. Historial de Git y Direcciones de Terceros

> [!CAUTION]
> **Registro de incidente de privacidad en Git:**  
> En los commits `f5eeb24` y `64a8606` del historial de Git se introdujo involuntariamente una dirección de billetera de un tercero obtenida durante consultas exploratorias a Hyperliquid.
> 
> - **Estado actual:** El archivo real fue eliminado del árbol de trabajo en `64a8606` y sustituido íntegramente por fixtures con datos 100 % sintéticos e inventados (`fixtures/hyperliquid_clearinghouse_synthetic.json`).
> - **Compromiso operativo:** Dicha dirección **no se vuelve a usar bajo ninguna circunstancia** en el código, pruebas, fixtures o documentación.
> - **Política de reescritura:** Por instrucción expresa del usuario, **no se reescribirá el historial de Git** (`git reset --hard` / `git push --force`) sin su confirmación expresa previa.
