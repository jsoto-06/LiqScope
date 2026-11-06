# Supuestos del Modelo Matemático y Fuentes — LiqScope

> [!IMPORTANT]
> Niveles de liquidación estimados modelados a partir de Open Interest agregado bajo el supuesto de assumed_long_ratio = 0.50 y parámetros arbitrarios de MMR (MMR < 1/L). El tramo 5x es ilustrativo. Se ignoran comisiones de trading, comisiones de liquidación, tasas de financiación y mecánicas de colateral de margen cruzado. No refleja posiciones individuales reales, precios de entrada reales ni sesgo direccional del mercado.

---

## 1. Clasificación del Origen de Datos (`DataOrigin`)

El modelo clasifica el origen de los datos según el ADR-011 en dos categorías epistemológicas estrictas:

1. **Datos Observados (`OBSERVED`):**
   - **Fuentes:** Eventos de liquidación forzosa emitidos por los WebSockets de los exchanges (Binance `forceOrder`, Bybit `allLiquidation`) y telemetría directa de mercado.
   - **Fundamento:** Información emitida por el exchange y recibida directamente sin modelado matemático interpolado.
   - **Limitación y Supuesto de `forceOrder` en Binance (NO VERIFICADA):** La cifra de frecuencia de **1000 ms** y la premisa de entrega de únicamente la liquidación más grande por segundo proceden de referencias habituales pero **carecen de cita literal verificable**, dado que la página web oficial de documentación (`developers.binance.com`) devuelve `HTTP 202` (desafío anti-bot Cloudflare). Por tanto, se etiqueta formalmente como **supuesto no verificado**. En consecuencia, el volumen público de `forceOrder` se trata operativamente como un muestreo conservador (límite inferior) del volumen total liquidado en Binance, no el 100 % absoluto.
2. **Datos Modelados (`MODELED`):**
   - **Fuentes:** Mapa de calor analítico de liquidaciones (Heatmap).
   - **Fundamento:** Distribución teórica del Open Interest agregado a través de escalones de apalancamiento supuestos y tasas de margen de mantenimiento arbitrarias (MMR < 1/L).

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

---

## 6. Supuestos y Límites del Modelo Analítico de Liquidaciones (Fase 4)

1. **Tasas de Margen de Mantenimiento (MMR) Arbitrarias:**
   Los valores asignados por escalón (5x: 0.040, 10x: 0.020, 25x: 0.010, 50x: 0.005, 100x: 0.004) son **supuestos analíticos arbitrarios** calibrados matemáticamente para garantizar la condición estricta $\text{MMR} < 1/L$ ($\Delta = 1/L - \text{MMR} > 0$). No constituyen ni reflejan las tablas contractuales oficiales por tramos de nocional de Binance Futures.
2. **Nivel 5x Ilustrativo:**
   El nivel de apalancamiento de 5x se incluye con fines meramente pedagógicos e ilustrativos para modelar horizontes conservadores; no representa la estructura real de participantes institucionales.
3. **Omisión de Comisiones y Margen Cruzado (Cross-Margin):**
   El cálculo modela posiciones aisladas lineales asumiendo que todo el Open Interest entró exactamente al precio de marca actual ($P_{\text{entry}} = P_{\text{mark}}$). El modelo **ignora sistemáticamente**:
   - Comisiones de apertura, cierre y corretaje por liquidación forzosa.
   - Tasas de financiamiento acumuladas (*funding rate*).
   - Efectos del margen cruzado (*cross-margin*), donde balances libres o colaterales multidivisa amortiguan el precio real de quiebra.
4. **Supuesto de Simetría Neutra (`assumed_long_ratio = 0.50`):**
   La partición al 50 % entre largos y cortos es un supuesto teórico de diseño. No refleja el sesgo direccional neto (*market skew*) ni el sentimiento real del libro de posiciones.



---

## 7. Estrategia de Caché de Datos de Mercado y Telemetría (`cached`, `data_age_sec`)

Para cumplir con el presupuesto de tasa de Binance Futures (2.400 weight/min) y prevenir denegación de servicio o bloqueos HTTP 429/418 ante peticiones concurrentes:

1. **Caché en Memoria con TTL (Time To Live):**
   - Las consultas de mercado (`markPrice` y `openInterest`) se almacenan en una caché en memoria por símbolo con un TTL configurable predeterminado de **10.0 segundos** (`market_data_cache_ttl_sec`).
2. **Telemetría en la Respuesta de la API:**
   - **`cached` (`bool`):** Indica si los datos de mercado utilizados para modelar el snapshot fueron recuperados de la caché local (`true`) o consultados en vivo a Binance en dicha petición (`false`).
   - **`data_age_sec` (`float`):** Tiempo transcurrido en segundos (con precisión decimal) desde que los datos de mercado fueron obtenidos del exchange remoto hasta la emisión de la respuesta actual. Si los datos fueron obtenidos en la petición activa, `data_age_sec = 0.0`.
