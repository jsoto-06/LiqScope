# Manual de Usuario LiqScope — Terminal Institucional de Derivados y Liquidaciones

Bienvenido a la guía oficial y manual de usuario integral de **LiqScope**, la terminal analítica cuantitativa de derivados cripto y modelado de zonas de liquidación forzada en tiempo real.

---

## Índice

1. [¿Qué es LiqScope y cómo funciona el modelado de liquidaciones?](#1-qué-es-liqscope-y-cómo-funciona-el-modelado-de-liquidaciones)
2. [Garantía de Transparencia: Telemetría Real vs. Modelado Analítico](#2-garantía-de-transparencia-telemetría-real-vs-modelado-analítico)
3. [Instalación y Puesta en Marcha](#3-instalación-y-puesta-en-marcha)
   - [3.1. En Contenedor Docker (Recomendado)](#31-en-contenedor-docker-recomendado)
   - [3.2. En Windows (1 Clic)](#32-en-windows-1-clic)
   - [3.3. Desde Consola Python](#33-desde-consola-python)
4. [Recorrido Visual por el Workspace ("Terminal Heat")](#4-recorrido-visual-por-el-workspace-terminal-heat)
   - [4.1. Barra de Navegación Superior y Telemetría en Vivo](#41-barra-de-navegación-superior-y-telemetría-en-vivo)
   - [4.2. Gráfico TradingView (Lightweight Charts) con Capas Térmicas](#42-gráfico-tradingview-lightweight-charts-con-capas-térmicas)
   - [4.3. Horizontes Temporales de Acumulación (12h a 3m)](#43-horizontes-temporales-de-acumulación-12h-a-3m)
   - [4.4. Súper Gráficos: Sub-paneles de Open Interest y Funding Sincronizados](#44-súper-gráficos-sub-paneles-de-open-interest-y-funding-sincronizados)
   - [4.5. Escalera DOM de Clústeres y Bins de Liquidación](#45-escalera-dom-de-clústeres-y-bins-de-liquidación)
   - [4.6. Bento Tiles de Riesgo y Ratio Cuentas Long/Short](#46-bento-tiles-de-riesgo-y-ratio-cuentas-longshort)
   - [4.7. Matriz Térmica Multi-Exchange de Tasas de Financiación](#47-matriz-térmica-multi-exchange-de-tasas-de-financiación)
   - [4.8. Screener de Mercado y Radar de Ballenas (OI Surge)](#48-screener-de-mercado-y-radar-de-ballenas-oi-surge)
   - [4.9. Tracker Institucional de ETFs Spot (Bitcoin & Ethereum)](#49-tracker-institucional-de-etfs-spot-bitcoin--ethereum)
   - [4.10. Simulador Interactivo de Margen de Mantenimiento (MMR)](#410-simulador-interactivo-de-margen-de-mantenimiento-mmr)
   - [4.11. Monitor de Alertas, WebSockets y Bot de Telegram](#411-monitor-de-alertas-websockets-y-bot-de-telegram)
5. [Guía Completa de la API REST v1](#5-guía-completa-de-la-api-rest-v1)
6. [Preguntas Frecuentes (FAQ)](#6-preguntas-frecuentes-faq)
7. [Aviso Regulatorio Institucional](#7-aviso-regulatorio-institucional)

---

## 1. ¿Qué es LiqScope y cómo funciona el modelado de liquidaciones?

En los contratos de futuros perpetuos con margen cruzado o aislado, cuando las pérdidas latentes de una posición superan el margen disponible y alcanzan la tasa de margen de mantenimiento (*Maintenance Margin Rate* o MMR), el motor de riesgo del exchange ejecuta una **liquidación forzosa**:
* **Liquidación de una posición Long (Compradora):** El exchange lanza una orden de venta de mercado a través del libro de órdenes, provocando un impacto bajista repentino.
* **Liquidación de una posición Short (Vendedora):** El exchange lanza una orden de compra de mercado, provocando un impacto alcista repentino.

La agrupación densa de posiciones apalancadas en niveles específicos crea **bolsas masivas de liquidez forzada (Liquidity Pools)**. Los creadores de mercado (*Market Makers*), operadores institucionales y algoritmos de alta frecuencia identifican estos niveles y tienden a impulsar el precio hacia ellos para absorber contrapartida abundante (*Liquidity Sweeps*).

**LiqScope** proyecta en tiempo real estos mapas de calor de liquidación, permitiendo al operador anticipar dónde se encuentran los mayores focos magnéticos de atracción y los niveles críticos de soporte o resistencia forzada.

---

## 2. Garantía de Transparencia: Telemetría Real vs. Modelado Analítico

LiqScope sigue un protocolo estricto de honestidad cuantitativa y transparencia matemática:

| Métrica / Parámetro | Tipo | Fuente Oficial | Explicación Técnica |
| :--- | :---: | :--- | :--- |
| **Precio Mark (`mark_price`)** | **100 % REAL** | Binance Futures API (`/fapi/v1/premiumIndex`) | Precio de referencia fiduciario ponderado por índice para el cálculo oficial de liquidaciones del exchange. |
| **Interés Abierto (`open_interest`)** | **100 % REAL** | Binance Futures API (`/fapi/v1/openInterest`) | Suma total oficial de contratos vigentes en dólares y monedas en este instante. |
| **Ratio de Cuentas L/S (`globalLongShortAccountRatio`)** | **100 % REAL** | Binance Futures API (`/futures/data/globalLongShortAccountRatio`) | Porcentaje neto real de cuentas minoristas e institucionales posicionadas al alza vs a la baja. |
| **Tasas de Financiación (Funding Rates)** | **100 % REAL** | Binance & Bybit REST/WebSockets | Tasas de financiación en vivo intercambiadas entre posiciones largas y cortas cada 8 horas. |
| **Tiers Oficiales de Margen (MMR)** | **100 % REAL** | Normativa Oficial Binance Tiers 1–10+ | Escalamiento normativo oficial del margen de mantenimiento según el tamaño nocional de la posición. |
| **Flujos Institucionales de ETFs** | **100 % REAL** | Registros Oficiales SEC 13F / Emisores | Tenencias físicas en custodia auditada y suscripciones/redenciones netas diarias de los fondos spot. |
| **Zonas y Precios de Liquidación** | **MODELADO** | Motor Cuantitativo LiqScope | Proyección analítica del Open Interest en escalones discretos de apalancamiento respetando las ecuaciones oficiales de liquidación forzada. |

> [!NOTE]
> Ningún exchange de derivados publica las carteras individuales ni los precios de entrada exactos de sus usuarios por privacidad financiera y secreto bancario. LiqScope deriva estos niveles con rigor analítico sobre la telemetría real del libro.

---

## 3. Instalación y Puesta en Marcha

### 3.1. En Contenedor Docker (Recomendado)
Es la opción óptima para entornos de producción en Linux, macOS o Windows con Docker Desktop:
```bash
git clone https://github.com/jsoto-06/LiqScope.git
cd LiqScope
docker compose up -d --build
```
El panel web estará accesible de inmediato en: **`http://localhost:8000`**.

### 3.2. En Windows (1 Clic)
En la carpeta raíz del proyecto, simplemente haz doble clic en:
👉 **`start_dashboard.bat`**
El script iniciará el servidor local y abrirá tu navegador predeterminado.

### 3.3. Desde Consola Python
Requiere Python 3.12 o superior:
```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e .
uvicorn liqscope.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

---

## 4. Recorrido Visual por el Workspace ("Terminal Heat")

### 4.1. Barra de Navegación Superior y Telemetría en Vivo
* **Selector de Símbolo:** Alterna instantáneamente entre `BTCUSDT` y `ETHUSDT` (o pares adicionales vía URL).
* **Precio Mark Live:** Visualización en neón cian centrado en el mercado con actualización reactiva.
* **Modo de Datos:** `Live Feed` (conexión a exchanges) o `Demo` (entorno sintético fuera de línea).
* **Temporizador Regresivo (Auto-refresco 120s):** Contador regresivo visible que sincroniza la profundidad del libro cada 2 minutos.
* **Botón Refrescar (Icono ⟳):** Permite forzar una actualización instantánea en cualquier segundo.

### 4.2. Gráfico TradingView (Lightweight Charts) con Capas Térmicas
* **Motor de Velas OHLCV:** Desarrollado sobre TradingView Lightweight Charts `v4.2.0`, permitiendo paneo horizontal continuo, zoom vertical y horizontal, y ajuste automático del tiempo.
* **Lienzo Térmico Canvas 2D:** Capa transparente renderizada por encima de la cuadrícula y debajo del cursor de precios, garantizando 60 FPS estables.
* **Paletas de Color Disponibles:**
  * **🔥 LiqScope Turbo (Por Defecto):** Escala cromática de alta resolución inspirada en terminales de grado institucional.
    - Azul Marino Profundo: Densidad térmica baja (< 20%).
    - Cian Eléctrico: Densidad térmica moderada (20% – 50%).
    - Verde Esmeralda: Densidad térmica alta (50% – 80%).
    - Amarillo Neón / Foco Dorado: Densidad ultra alta / Epicentro (`MAX LIQ`).
  * **🟢🔴 Longs / Shorts:** Clasificación clásica en tonos verdes para liquidaciones de posiciones largas y rojas para cortas.
  * **⚡ Plasma Neón:** Esquema de alto contraste violeta-magenta para monitores OLED y sesiones nocturnas.
* **Control de Intensidad:** Ajusta la ganancia del gradiente térmico (`1.0x` a `2.5x`).
* **Botón Heatmap ON/OFF:** Permite ocultar temporalmente las bandas térmicas para examinar el gráfico de velas puro.

### 4.3. Horizontes Temporales de Acumulación (12h a 3m)
En la barra de herramientas del gráfico encontrarás el selector de horizonte:
* **⏱️ 12h & ⏱️ 24h (Intradía):** Capturan el apalancamiento agresivo (50x a 100x). Las bandas de liquidación se concentran muy cerca del precio Mark (a una distancia de 0.5% a 2%).
* **⏱️ 3d & ⏱️ 1w (Swing Trading):** Ponderan posiciones de medio plazo (25x a 50x), mostrando zonas de liquidez que resisten la volatilidad de varios días.
* **⏱️ 1m & ⏱️ 3m (Posiciones Macro):** Distribuyen el Open Interest hacia apalancamientos conservadores (5x a 10x), delineando los grandes suelos y techos de liquidación estructural del mercado.

### 4.4. Súper Gráficos: Sub-paneles de Open Interest y Funding Sincronizados
* **Sub-panel de Open Interest:** Muestra la evolución del interés abierto en dólares. Permite detectar si una subida de precio está respaldada por nueva entrada de capital apalancado o por cierre de posiciones cortas (*Short Squeeze*).
* **Sub-panel de Tasas de Financiación Históricas:** Histograma de barras sincronizado:
  * Barras verdes por encima de 0: Los largos pagan a los cortos (mercado con prima compradora).
  * Barras rojas por debajo de 0: Los cortos pagan a los largos (mercado con descuento o presión vendedora).

### 4.5. Escalera DOM de Clústeres y Bins de Liquidación
* **Selector de Bins:** Permite configurar la resolución de cada escalón (ej. `10 USD` o `25 USD` para ETH; `50 USD` o `100 USD` para BTC).
* **Badge `MAX LIQ`:** Rótulo dorado ámbar que parpadea sobre el clúster con mayor volumen concentrado de todo el libro visible.
* **Multiplicadores Dominantes (`[25x]`, `[50x]`, `[100x]`):** Informa cuál es el tramo de apalancamiento que tiene mayor peso en ese escalón.
* **Inspector de Clúster:** Al hacer clic en cualquier fila de la escalera se despliega el panel de detalle con el Tier MMR exacto, la distancia porcentual al precio Mark, el volumen estimado en millones de dólares y el riesgo de cascada.

### 4.6. Bento Tiles de Riesgo y Ratio Cuentas Long/Short
* **Shorts en Riesgo:** Volumen total nocional de liquidaciones cortas acumuladas por encima del precio actual.
* **Longs en Riesgo:** Volumen total nocional de liquidaciones largas acumuladas por debajo del precio actual.
* **Barra Dual Ratio Long/Short:** Conectada directamente a la telemetría oficial de Binance (`globalLongShortAccountRatio`), refleja el porcentaje real de operadores con posiciones alcistas versus bajistas.

### 4.7. Matriz Térmica Multi-Exchange de Tasas de Financiación
Ubicada en la pestaña **"Financiación"**:
* Compara las tasas de financiación de los principales activos en **Binance Futures** y **Bybit Linear**.
* Proyecta el **APR Anualizado** (tasa a 8 horas multiplicada por 1.095 periodos anuales).
* Cuenta atrás en vivo para la próxima liquidación de financiación.
* Alerta de **Sobrecalentamiento (*Overheat*)**: Si el APR excede el +30% o cae por debajo del -30%, la celda se resalta indicando condiciones extremas de mercado.

### 4.8. Screener de Mercado y Radar de Ballenas (OI Surge)
Ubicada en la pestaña **"Screener & Ballenas"**:
* Monitoriza más de **620 contratos perpetuos** en paralelo.
* **Barómetro de Amplitud:** Contabiliza el número y porcentaje de contratos en verde (*Advancers*) versus contratos en rojo (*Decliners*), ofreciendo una radiografía macro del sentimiento general del mercado.
* **Detección Algorítmica de Ballenas (OI Surge):**
  * 🐋 **ACUMULACIÓN:** Incremento agresivo de Open Interest acompañado de subida de precio.
  * 🐋 **DISTRIBUCIÓN:** Incremento agresivo de Open Interest acompañado de caída de precio.
  * ⚡ **SQUEEZE RISK:** Ratio de apalancamiento extremo respecto al volumen 24h.
* **Acción Rápida `🔍 Analizar`:** Permite saltar con un solo clic desde cualquier par del screener directamente a su gráfico de velas y mapa de liquidaciones.

### 4.9. Tracker Institucional de ETFs Spot (Bitcoin & Ethereum)
Ubicada en la pestaña **"ETFs Institucional"**:
* Seguimiento en vivo de los **10 ETFs de Bitcoin** y **8 ETFs de Ethereum** aprobados por la SEC.
* Visualiza el AUM total en dólares, las monedas físicas bajo custodia institucional y el flujo neto de la última jornada bursátil.
* **Gráfico de Flujos Netos Diarios:** Muestra las últimas 14 sesiones con barras verdes (inflows netos) y rojas (outflows netos).
* **Tabla Oficial de Fondos:** Desglose con ticker, emisor (BlackRock, Fidelity, Grayscale...), activos en custodia, comisión de gestión (*Expense Ratio*) y custodio institucional auditado (*Coinbase Prime, Fidelity Digital Assets, Gemini Trust*).

### 4.10. Simulador Interactivo de Margen de Mantenimiento (MMR)
Ubicada en la pestaña **"Simulador MMR"**:
* Permite ingresar cualquier precio de entrada y seleccionar el apalancamiento deseado (5x, 10x, 25x, 50x, 100x).
* Botón **"Usar Mark Actual"** para cargar de inmediato la cotización en vivo.
* Calcula con precisión milimétrica el precio de liquidación para Longs y Shorts respetando la fórmula oficial de Binance y su tier de margen correspondiente.

### 4.11. Monitor de Alertas, WebSockets y Bot de Telegram
* **Feed WebSocket de Liquidaciones:** Streaming en `/ws/liquidations` con eventos de liquidación forzada transmitidos en milisegundos.
* **Bot de Telegram:** Configurable mediante las variables `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en el archivo `.env`.
* Notifica de forma automática cuando el precio de mercado atraviesa un muro de liquidación significativo (`MAX LIQ`).

---

## 5. Guía Completa de la API REST v1

Todos los endpoints retornan respuestas estructuradas en formato JSON bajo el prefijo `/api/v1`.

### 5.1. Mapa de Calor de Liquidaciones
```http
GET /api/v1/heatmap/{symbol}?timeframe=24h&bin_size=50.0&ratio_mode=live
```
* **Parámetros de consulta:**
  - `timeframe`: `'12h'`, `'24h'`, `'3d'`, `'1w'`, `'1m'`, `'3m'`.
  - `bin_size`: Ancho del escalón en USD (ej. `50.0` para BTC, `10.0` para ETH).
  - `ratio_mode`: `'live'` (Binance real) o `'50_50'` (simétrico).

#### Ejemplo con cURL:
```bash
curl -s "http://localhost:8000/api/v1/heatmap/BTCUSDT?timeframe=24h&bin_size=50" | jq .
```

### 5.2. Matriz de Tasas de Financiación
```http
GET /api/v1/funding
```
Retorna la matriz de tasas multi-exchange, APR anualizado, tiempo restante en segundos para el próximo cobro y diagnóstico de sesgo de mercado.

### 5.3. Screener de Mercado y Radar de Ballenas
```http
GET /api/v1/screener
```
Retorna el barómetro de amplitud, top gainers, top losers, contratos con pico de acumulación de ballenas (`oi_surge`) y la lista completa de pares filtrados.

### 5.4. Tracker de ETFs Institucionales
```http
GET /api/v1/etfs
```
Retorna el balance consolidado de ETFs de Bitcoin y Ethereum, desglose de fondos individuales, flujos históricos y sentimiento institucional.

### 5.5. Velas Históricas y Sub-paneles
```http
GET /api/v1/klines/{symbol}?interval=1h&limit=100
GET /api/v1/klines/{symbol}/open-interest?interval=1h&limit=50
GET /api/v1/klines/{symbol}/funding-rate?limit=50
```

---

## 6. Preguntas Frecuentes (FAQ)

### ¿Cómo calcula LiqScope los niveles de liquidación institucional?
LiqScope toma el Open Interest oficial de Binance en vivo y lo distribuye en escalones de apalancamiento calibrados con rigor cuantitativo. Las zonas magnéticas clave y los niveles de liquidación coinciden matemáticamente porque respetan los tiers oficiales de margen (MMR) de Binance.

### ¿Por qué cambian las zonas de liquidación al cambiar el horizonte temporal?
Un operador intradía que abre con apalancamiento 50x o 100x tiene su precio de liquidación muy cerca del precio de entrada (a un 1% o 2%). Si la posición no se liquida en pocas horas, el operador suele cerrarla o mover su stop. Por tanto, en horizontes cortos (12h/24h) dominan los niveles cercanos con alto apalancamiento. En horizontes amplios (1m/3m) se acumulan posiciones de menor apalancamiento (5x-10x) con zonas de liquidación más distantes.

### ¿Por qué las liquidaciones Long están por debajo del precio y las Short por encima?
* Un operador en **Long** compra esperando que el precio suba. Si el precio cae por debajo de su margen, el sistema lo liquida forzosamente (precio de liquidación < precio de entrada).
* Un operador en **Short** vende esperando que el precio caiga. Si el precio sube por encima de su margen, es liquidado (precio de liquidación > precio de entrada).

### ¿La aplicación puede gestionar fondos o necesita mis claves privadas?
**Absolutamente no.** LiqScope es una herramienta de telemetría de solo lectura. No tiene conexión a billeteras, no ejecuta órdenes y no solicita credenciales secretas de trading.

---

## 7. Aviso Regulatorio Institucional

> [!IMPORTANT]
> **LECTURA PURA — FINES EDUCATIVOS E INFORMATIVOS:** LiqScope es una herramienta analítica cuantitativa de código abierto. La información desplegada no constituye asesoría de inversión, recomendación comercial ni solicitud de depósitos. Los mercados de derivados apalancados conllevan un alto riesgo de pérdida de capital. Opere siempre bajo su propia responsabilidad y gestión de riesgo.
