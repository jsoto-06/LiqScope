# Manual de Usuario LiqScope — Liquidation Heatmap & Telemetry

Bienvenido a la guía oficial y manual de usuario detallado de **LiqScope**, la herramienta de telemetría institucional y modelado analítico de zonas de liquidación para derivados cripto (**Binance Futures USDⓢ-M**).

---

## Índice

1. [¿Qué es LiqScope y cómo funciona?](#1-qué-es-liqscope-y-cómo-funciona)
2. [Transparencia de Datos: Realidad vs. Modelado](#2-transparencia-de-datos-realidad-vs-modelado)
3. [Cómo Iniciar LiqScope](#3-cómo-iniciar-liqscope)
4. [Recorrido Visual por el Dashboard ("Terminal Heat")](#4-recorrido-visual-por-el-dashboard-terminal-heat)
   - [4.1. Barra Superior de Telemetría](#41-barra-superior-de-telemetría)
   - [4.2. Controles de Filtrado y Granularidad](#42-controles-de-filtrado-y-granularidad)
   - [4.3. Escalera de Clústeres y Hotspots (CoinGlass-Style)](#43-escalera-de-clústeres-y-hotspots-coinglass-style)
   - [4.4. Bento Tiles de Riesgo y Ratio Long/Short en Vivo](#44-bento-tiles-de-riesgo-y-ratio-longshort-en-vivo)
   - [4.5. Zona de Mayor Magnetismo e Inspector de Clúster](#45-zona-de-mayor-magnetismo-e-inspector-de-clúster)
   - [4.6. Pestañas Secundarias (Modelo, Simulador MMR, Alertas)](#46-pestañas-secundarias-modelo-simulador-mmr-alertas)
5. [Granularidad Óptima de Bins: BTC vs. ETH](#5-granularidad-óptima-de-bins-btc-vs-eth)
6. [Guía de la API REST](#6-guía-de-la-api-rest)
7. [Preguntas Frecuentes (FAQ)](#7-preguntas-frecuentes-faq)
8. [Aviso Regulatorio Institucional](#8-aviso-regulatorio-institucional)

---

## 1. ¿Qué es LiqScope y cómo funciona?

En los mercados de futuros perpetuos, cuando una posición apalancada acumula pérdidas equivalentes a su margen de mantenimiento, el exchange ejecuta una **liquidación forzosa** mediante órdenes de mercado automáticas:
* Si se liquida una posición **Long**, el motor vende al mercado (presión bajista).
* Si se liquida una posición **Short**, el motor compra al mercado (presión alcista).

La acumulación masiva de órdenes de stop y liquidaciones en ciertos niveles de precio genera **bolsas de liquidez (pools)** que actúan como auténticos **imanes de precio**. Los grandes participantes (market makers, traders institucionales y algoritmos de alta frecuencia) suelen empujar el precio hacia estas zonas para absorber liquidez en mechas rápidas (*liquidity sweeps*).

**LiqScope** proyecta en tiempo real estos mapas de calor sobre los pares **BTC/USDT** y **ETH/USDT**, permitiéndote identificar con precisión milimétrica dónde se encuentran las mayores concentraciones de riesgo.

---

## 2. Transparencia de Datos: Realidad vs. Modelado

Una de las premisas fundamentales de LiqScope es la honestidad técnica:

| Métrica / Dato | Naturaleza | Fuente Oficial | Descripción |
| :--- | :---: | :--- | :--- |
| **Precio Mark (`mark_price`)** | **100 % REAL** | Binance Futures API (`/fapi/v1/premiumIndex`) | Precio de referencia fiduciario ponderado por índice para el cálculo de liquidaciones. |
| **Interés Abierto (`open_interest`)** | **100 % REAL** | Binance Futures API (`/fapi/v1/openInterest`) | Suma total oficial de contratos vigentes abiertos en el exchange en este instante. |
| **Ratio de Cuentas L/S (`globalLongShortAccountRatio`)** | **100 % REAL** | Binance Futures API (`/futures/data/globalLongShortAccountRatio`) | Porcentaje neto real de cuentas netas en largo vs. en corto (ej. 77.9 % Long / 22.1 % Short). |
| **Tasas MMR Oficiales** | **100 % REAL** | Normativa Binance Tiers 1–5 | Tasa oficial de margen de mantenimiento exigida por apalancamiento (5x=4%, 10x=2%, 25x=1%, 50x=0.5%, 100x=0.4%). |
| **Zonas y Precios de Liquidación** | **MODELADO** | Motor Analítico LiqScope | Proyección matemática del Open Interest en escalones de apalancamiento discretos respetando los invariantes del exchange. |

> [!NOTE]
> Ningún exchange de derivados del mundo comparte las identidades o precios de entrada exactos de sus usuarios por privacidad financiera. Al igual que CoinGlass o Kingfisher, LiqScope deriva estos niveles con rigor analítico sobre la telemetría real del libro.

---

## 3. Cómo Iniciar LiqScope

### Inicio Rápido en Windows
Haz doble clic en el archivo:
```powershell
start_dashboard.bat
```
El navegador se abrirá automáticamente en: `http://localhost:8000/`.

### Inicio desde Consola / Terminal
```powershell
py -3.12 -m uvicorn liqscope.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

---

## 4. Recorrido Visual por el Dashboard ("Terminal Heat")

### 4.1. Barra Superior de Telemetría
* **Selector de Símbolo:** Alterna entre `BTCUSDT` y `ETHUSDT` con un solo clic. El dashboard reconfigura dinámicamente los bins y la escala de precios.
* **Modo de Datos:**
  * **Live Feed:** Sincronizado en tiempo real con los servidores de Binance Futures.
  * **Demo:** Modo fuera de línea con datos sintéticos representativos para pruebas o demostraciones.
* **Auto-refresco (120 s):** Temporizador regresivo visible (`Auto: 02:00 -> 01:59...`) que actualiza la telemetría cada 2 minutos sin recargar la página.
* **Botón Refrescar (Icono ⟳):** Permite forzar una actualización inmediata de mercado.
* **Precio Mark Live:** Valor actual en neón cian centrado en el mercado.

### 4.2. Controles de Filtrado y Granularidad
* **Selector de Bins:** Permite elegir el ancho de cada celda (`10 USD`, `25 USD`, `50 USD`, `100 USD`, `250 USD`, `500 USD`).
* **Rango Min/Max USD:** Permite acotar la ventana de análisis para enfocar únicamente un rango específico de precio.
* **Filtro de Apalancamiento (`Todos`, `5x`, `10x`, `25x`, `50x`, `100x`):** Al seleccionar un multiplicador específico, la escalera filtra instantáneamente las filas mostrando solo los niveles que contienen dicho apalancamiento.

### 4.3. Escalera de Clústeres y Hotspots (CoinGlass-Style)
Cada fila de la matriz representa un escalón de precio con:
1. **Rango y Precio Central:** Muestra el precio promedio del clúster (ej. `$2,165` o `$73,475`) y el intervalo `[Min - Max]`.
2. **Badge `🔥 MAX LIQ`:** Destaca en dorado ámbar con resplandor pulsante la zona con mayor volumen concentrado de todo el libro visible.
3. **Barra de Densidad Térmica:** Barra de progreso proporcional al clúster dominante:
   * **Dorado Ámbar:** `SHORT POOL` (posiciones cortas situadas por encima del Mark).
   * **Verde Esmeralda:** `LONG POOL` (posiciones largas situadas por debajo del Mark).
4. **Volumen en Millones de USD:** Volumen acumulado del clúster (ej. `$1,229.25M`).
5. **Pill de Apalancamiento Dominante:** Etiqueta explícita con el multiplicador responsable del mayor peso en ese bin (ej. `[25x]`, `[50x]`, `[100x]`).
6. **Láser Neón del Precio Mark:** Línea divisoria en tiempo real que separa los pools superiores (Shorts) de los inferiores (Longs).

### 4.4. Bento Tiles de Riesgo y Ratio Long/Short en Vivo
* **Shorts en Riesgo:** Volumen total de posiciones en corto que serían barridas si el precio sube a las resistencias.
* **Longs en Riesgo:** Volumen total de posiciones en largo que serían liquidadas si el precio perfora los soportes.
* **Ratio Long / Short OI:** Barra dual segmentada alimentada directamente por el endpoint `globalLongShortAccountRatio` de Binance. Muestra el porcentaje exacto de cuentas del exchange posicionadas al alza vs. a la baja (ej. `77.9% Long / 22.1% Short`).

### 4.5. Zona de Mayor Magnetismo e Inspector de Clúster
La tarjeta destacada identifica el foco de atracción más potente del mercado:
* **Precio Objetivo:** Nivel exacto del clúster.
* **Distancia al Mark:** Variación porcentual y en USD necesaria para alcanzar el clúster (ej. `-3.14% (~$70.22)`).
* **Botón "Inspeccionar Desglose Institucional del Clúster":** Al hacer clic (o al pulsar sobre cualquier fila de la escalera), se despliega el panel técnico con:
  * **Tier / Apalancamiento:** Multiplicador dominante y tasa MMR exigida.
  * **Delta Requerido:** Distancia porcentual de seguridad.
  * **Volumen Estimado:** Monto total en millones de USD.
  * **Riesgo de Cascada:** Clasificación automática del riesgo (`CRÍTICO / INMEDIATO`, `ELEVADO` o `MODERADO`).

### 4.6. Pestañas Secundarias (Modelo, Simulador MMR, Alertas)
* **Modelo & Datos:** Transparencia con enlaces directos a las APIs de Binance y documentación de fórmulas de liquidación.
* **Niveles MMR & Simulador:** Permite simular qué ocurriría con una posición personal introduciendo un precio de entrada o usando el botón **"Usar Mark Actual"**.
* **Alertas:** Monitor de eventos de liquidación y niveles críticos.

---

## 5. Granularidad Óptima de Bins: BTC vs. ETH

Debido a la gran diferencia en el precio unitario entre Bitcoin y Ethereum, la elección del tamaño de bin es crucial:

* **Para BTCUSDT (~$75,000 USD):**
  * **Recomendado:** `50 USD` o `100 USD`.
  * Un bin de 50 USD representa apenas un `0.066 %` del precio, separando con máxima resolución los niveles de 5x hasta 100x.
* **Para ETHUSDT (~$2,200 USD):**
  * **Recomendado:** `10 USD` (el dashboard lo selecciona automáticamente al elegir ETH).
  * Con 50 USD, un bin abarcaría más del `2.2 %` del precio, fusionando 50x y 100x en un solo bloque. Con **10 USD**, cada escalón de apalancamiento queda perfectamente aislado y legible.

---

## 6. Guía de la API REST

LiqScope expone una API REST moderna construida sobre FastAPI con caché TTL en memoria y protección single-flight contra sobrecargas.

### Endpoints Principales

#### 1. Consulta del Mapa de Calor
```http
GET /api/v1/heatmap/{symbol}
```
* **Parámetros de consulta (Query params):**
  * `symbol` *(ruta)*: `BTCUSDT` o `ETHUSDT`.
  * `bin_size` *(opcional, float)*: Tamaño del bin en USD (defecto: `50.0`).
  * `min_price` *(opcional, float)*: Límite inferior del rango de precio a incluir.
  * `max_price` *(opcional, float)*: Límite superior del rango de precio a incluir.
  * `ratio_mode` *(opcional, string)*: `'live'` (por defecto, lee el ratio en tiempo real de Binance) o `'neutral'` (utiliza 50/50).
  * `assumed_long_ratio` *(opcional, float)*: Ratio personalizado entre `0.0` y `1.0`. Si se pasa un valor distinto de `0.50`, tiene prioridad y activa `ratio_source='custom'`.
  * `source` *(opcional, string)*: `'live'` (Binance) o `'demo'` (datos de prueba).

#### Ejemplo con cURL
```bash
curl -s "http://localhost:8000/api/v1/heatmap/ETHUSDT?bin_size=10.0&ratio_mode=live"
```

#### Ejemplo con Python
```python
import httpx

response = httpx.get(
    "http://localhost:8000/api/v1/heatmap/BTCUSDT", params={"bin_size": 50.0, "ratio_mode": "live"}
)
data = response.json()

print(f"Mark: ${data['current_price']}")
print(
    f"Ratio Binance: {data['long_account_ratio'] * 100:.1f}% Long / {data['short_account_ratio'] * 100:.1f}% Short"
)

for b in data["bins"]:
    print(
        f"Bin ${b['price_mid']}: ${b['estimated_volume_usd'] / 1e6:.1f}M (Dominante: {b['dominant_leverage']}x)"
    )
```

#### 2. Símbolos Soportados y Bins Recomendados
```http
GET /api/v1/symbols
```
Respuesta:
```json
[
  {"symbol": "BTCUSDT", "default_bin_size": 50.0},
  {"symbol": "ETHUSDT", "default_bin_size": 10.0}
]
```

#### 3. Chequeo de Salud
```http
GET /health
```
Respuesta:
```json
{"status": "ok", "env": "development"}
```

---

## 7. Preguntas Frecuentes (FAQ)

### ¿Por qué CoinGlass y LiqScope muestran números similares pero no idénticos?
CoinGlass y LiqScope toman el mismo Open Interest oficial de Binance en vivo. Sin embargo, los pesos exactos asignados a cada tramo de apalancamiento (ej. si el tramo de 25x tiene un peso de 30 % o 28 %) son supuestos de distribución calibrados internamente. Las zonas magnéticas clave y los niveles de liquidación coinciden matemáticamente porque ambos respetan los tiers oficiales de margen de Binance.

### ¿Por qué las liquidaciones Long están por debajo del precio y las Short por encima?
* Un operador en **Long** compra esperando que el precio suba. Si el precio cae por debajo de su margen, el sistema lo liquida forzosamente (precio de liquidación < precio de entrada).
* Un operador en **Short** vende esperando que el precio caiga. Si el precio sube por encima de su margen, es liquidado (precio de liquidación > precio de entrada).

### ¿La aplicación puede gestionar fondos o necesita mis claves privadas?
**Absolutamente no.** LiqScope no tiene conexión a billeteras, no ejecuta órdenes y no solicita credenciales secretas. Solo realiza lecturas públicas de mercado.

---

## 8. Aviso Regulatorio Institucional

> [!IMPORTANT]
> **LECTURA PURA — FINES EDUCATIVOS E INFORMATIVOS:** LiqScope es una herramienta analítica cuantitativa de código abierto. La información desplegada no constituye asesoría de inversión, recomendación comercial ni solicitud de depósitos. Los mercados de derivados apalancados conllevan un alto riesgo de pérdida de capital. Opere siempre bajo su propia responsabilidad y gestión de riesgo.
