# LiqScope — Crypto Liquidation Heatmap

<p align="center">
  <a href="#-español"><b>🇪🇸 Versión en Español</b></a> &nbsp;|&nbsp; 
  <a href="#-english"><b>🇬🇧 English Version</b></a>
</p>

---

# 🇪🇸 Español

## LiqScope — Mapa de Calor de Liquidaciones Cripto

> [!IMPORTANT]
> **Aviso de Responsabilidad:** Herramienta analítica de solo lectura con fines educativos e informativos. No constituye asesoramiento financiero ni señales de compra o venta. LiqScope **NO** gestiona fondos, **NO** ejecuta órdenes ni solicita claves privadas o API keys con permisos de trading.

---

### 1. Confirmación de Origen y Realidad de los Datos

Una de las dudas fundamentales en los mapas de calor de liquidaciones es si la información proyectada es **real**:

#### ¿Qué datos son 100 % REALES en vivo?
* **Precio Mark (`mark_price`) en tiempo real:** Obtenido directamente de los servidores oficiales de producción de **Binance Futures USDⓈ-M** (`https://fapi.binance.com/fapi/v1/premiumIndex`).
* **Interés Abierto Total (`total_open_interest_usd`):** Volumen global real oficial de contratos de futuros abiertos en el exchange en este instante (`https://fapi.binance.com/fapi/v1/openInterest`). Actualmente representa miles de millones de dólares (ej. ~95.000 BTC o ~$7.700M USD).
* **Parámetros Oficiales de Margen (MMR):** Escalones de margen de mantenimiento basados en la normativa oficial de apalancamiento de Binance.

#### ¿Por qué las zonas de liquidación son un MODELO analítico?
Ningún exchange de derivados del mundo (Binance, Bybit, OKX, etc.) publica las posiciones individuales ni los precios de entrada de cada usuario por secreto bancario y protección de la privacidad de sus clientes.

Por ello, plataformas profesionales como LiqScope, Coinglass o Kingfisher utilizan **modelos analíticos matemáticos**:
1. Toman el **Open Interest 100 % real** del mercado.
2. Lo distribuyen en los tramos de apalancamiento habituales del mercado (5x, 10x, 25x, 50x y 100x).
3. Aplican las fórmulas exactas de liquidación forzada de Binance:
   $$\text{Liquidación Long} = P_{\text{entrada}} \times \left(1 - \frac{1}{L} + \text{MMR}\right)$$
   $$\text{Liquidación Short} = P_{\text{entrada}} \times \left(1 + \frac{1}{L} - \text{MMR}\right)$$
4. Agrupan el volumen acumulado en escalones o "bins" de precio (ej. 50 USD) para identificar dónde se concentran las mayores bolsas de liquidez.

---

### 2. Cómo Usar la Aplicación (Modo Súper Fácil)

#### Opción A: Inicio en 1 Clic (Recomendado en Windows)
En la carpeta raíz del proyecto, simplemente haz **doble clic en el archivo:**
👉 **`start_dashboard.bat`**

Este script ejecutará el servidor local y **abrirá automáticamente tu navegador web** en:
🔗 **`http://localhost:8000/`**

#### Opción B: Inicio desde la Terminal
```powershell
# Iniciar el servidor FastAPI
py -3.12 -m uvicorn liqscope.api.app:create_app --factory --host 0.0.0.0 --port 8000
```
Luego abre tu navegador en [http://localhost:8000](http://localhost:8000).

---

### 3. Funcionalidades del Panel Visual ("Terminal Heat")

Al abrir [http://localhost:8000](http://localhost:8000), tendrás acceso al panel gráfico institucional interactivo:

1. **Auto-actualización cada 2 minutos (120 s):**
   * Consulta automática a Binance cada **120 segundos** en segundo plano con temporizador en vivo (`Auto: 02:00 -> 01:59...`) y hora exacta de sincronización.
   * Botón de actualización manual instantánea.
2. **Telemetría de Cuentas L/S 100% Real de Binance:**
   * Conexión directa a `globalLongShortAccountRatio`. Rompe la simetría artificial de 50/50 y proyecta las bolsas con los porcentajes reales del exchange (ej. 77.9% Long / 22.1% Short para ETH).
3. **Escalera de Clústeres y Hotspots (Estilo CoinGlass):**
   * 🔥 **Badge `MAX LIQ`:** Destaque pulsante dorado ámbar en el clúster con mayor liquidez concentrada del mercado.
   * **Multiplicador Dominante por Fila:** Badges explícitos (`[25x]`, `[50x]`, `[100x]`) indicando qué apalancamiento domina cada escalón.
   * **Inspector de Clúster Interactivo:** Al hacer clic en cualquier fila de la escalera o en el botón de foco de atracción, se despliega el desglose institucional (Tier MMR, Delta al Mark, Volumen USD y Nivel de Riesgo de Cascada).
   * **Láser de Precio Mark Live:** Línea neón cian divisoria en tiempo real entre Short Pools y Long Pools.
   * **Granularidad Óptima Automática:** Bins de `10 USD` para ETHUSDT y `50 USD` para BTCUSDT.
4. **Navegación Multi-Pestaña Institucional:**
   * 🔥 **Mapa de Calor:** Matriz completa, bento tiles de riesgo y zona de mayor magnetismo.
   * 📊 **Modelo & Datos:** Protocolo de integridad y transparencia criptográfica.
   * 📐 **Niveles MMR & Simulador:** Simulador interactivo con botón "Usar Mark Actual" y tabla de tiers de Binance.
   * 🔔 **Alertas:** Monitor de barridas de liquidación y niveles dinámicos.
   * 📖 **Manual de Usuario:** Guía técnica y operativa completa integrada en el panel (también disponible en [`MANUAL.md`](MANUAL.md) y [`/manual`](http://localhost:8000/manual)).

---

### 4. Configuración (`.env`)

LiqScope utiliza `pydantic-settings` para la gestión segura de configuración. Para personalizar parámetros, crea un archivo `.env` en la raíz copiando `.env.example`:

```bash
cp .env.example .env
```

| Variable | Descripción | Valor por defecto | Opciones válidas |
| :--- | :--- | :--- | :--- |
| `LIQSCOPE_ENV` | Entorno de ejecución | `development` | `development`, `production`, `test`, `demo` |
| `BINANCE_FUTURES_BASE_URL` | URL de la API de Binance Futures | `https://fapi.binance.com` | URL REST oficial o mock |
| `SERVER_HOST` | Host para el servidor HTTP | `0.0.0.0` | IP local o `127.0.0.1` |
| `SERVER_PORT` | Puerto de escucha | `8000` | Entero (ej. `8000`, `8080`) |
| `LIQSCOPE_CORS_ORIGINS` | Orígenes permitidos (CORS) | `["http://localhost:5173", "http://127.0.0.1:5173"]` | Lista JSON de dominios explícitos |
| `STORAGE_BACKEND` | Base de datos | `sqlite` | `sqlite`, `postgres` |
| `DATABASE_PATH` | Ruta de base de datos SQLite | `liqscope.db` | Ruta a archivo local |

> [!NOTE]
> Para consultar datos en vivo de Binance **no se necesitan claves de API** (`API Key` ni `API Secret`). LiqScope únicamente utiliza los endpoints públicos de mercado de Binance Futures.

---

### 5. Endpoints de la API REST

Además del panel visual, LiqScope expone una API REST canónica versionada:

* **Visualizador Web:** `GET /` (Dashboard visual interactivo).
* **Manual de Usuario:** `GET /manual` o [`MANUAL.md`](MANUAL.md) (Guía detallada de uso y telemetría).
* **Símbolos y Bins Recomendados:** `GET /api/v1/symbols` (Retorna pares soportados y su `default_bin_size`).
* **Mapa de Calor:** `GET /api/v1/heatmap/{symbol}`
  * Parámetros de consulta:
    * `min_price`: Límite inferior de precio (float).
    * `max_price`: Límite superior de precio (float).
    * `bin_size`: Tamaño del bin en USD (ej. `10.0` para ETH, `50.0` para BTC).
    * `ratio_mode`: `'live'` (Binance live account ratio) o `'neutral'` (estático 50/50).
    * `assumed_long_ratio`: Ratio personalizado (0.0 a 1.0) con prioridad sobre `ratio_mode`.
    * `source`: `'live'` (Binance) o `'demo'` (sintético).
  * Campos de respuesta adicionales:
    * `dominant_leverage` y `leverages`: Identificación del apalancamiento que compone cada bin.
    * `long_account_ratio` y `short_account_ratio`: Telemetría real de cuentas de Binance.
    * `cached` y `data_age_sec`: Estado de caché TTL y edad de datos.
* **Salud del Servidor:** `GET /health` (Estado `{"status": "ok", "env": "..."}`).
* **Documentación Interactiva (Swagger UI):** `GET /docs`
* **Especificación ReDoc:** `GET /redoc`

---

### 6. Instalación y Entorno de Desarrollo

#### Requisitos previos
- **Python 3.12+** instalado.
- **Git** instalado.

#### Configuración del entorno virtual
```powershell
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

# 3. Instalar dependencias en modo editable con herramientas de desarrollo
pip install -e .[dev]
```

#### Comprobaciones de Calidad y Tests (100 % Cobertura)
```powershell
# 1. Formateo y linter de código (Ruff)
py -3.12 -m ruff check src tests
py -3.12 -m ruff format --check src tests

# 2. Tipado estricto (Mypy)
py -3.12 -m mypy src tests

# 3. Suite completa de tests con reporte de cobertura (140 tests)
py -3.12 -m pytest --cov=liqscope --cov-report=term-missing
```

---

<br>

---

# 🇬🇧 English

## LiqScope — Crypto Liquidation Heatmap

> [!IMPORTANT]
> **Disclaimer:** Read-only analytical tool for educational and informational purposes. Does not constitute financial advice or buy/sell signals. LiqScope **DOES NOT** manage funds, **DOES NOT** execute orders, and **DOES NOT** request private keys or API keys with trading permissions.

---

### 1. Data Origin & Verification

One of the most important questions regarding liquidation heatmaps is whether the displayed data is **real**:

#### What data is 100% Live (OBSERVED)?
* **Real-time Mark Price (`mark_price`):** Fetched directly from official **Binance Futures USDⓈ-M** production servers (`https://fapi.binance.com/fapi/v1/premiumIndex`).
* **Total Open Interest (`total_open_interest_usd`):** Official real aggregate volume of open futures contracts on the exchange right now (`https://fapi.binance.com/fapi/v1/openInterest`). Currently represents billions of USD (e.g., ~95,000 BTC or ~$7,700M USD).
* **Official Margin Parameters (MMR):** Maintenance Margin Rate brackets based on official Binance leverage tiers.

#### Why are liquidation zones an analytical MODEL?
No derivatives exchange in the world (Binance, Bybit, OKX, etc.) publishes individual customer orders or exact entry prices due to banking privacy and confidentiality laws.

Therefore, institutional platforms such as LiqScope, Coinglass, or Kingfisher use **mathematical analytical models**:
1. Take the **100% real Open Interest** from the market.
2. Distribute it across the primary market leverage tiers (5x, 10x, 25x, 50x, 100x).
3. Apply official Binance forced liquidation formulas:
   $$\text{Long Liquidation} = P_{\text{entry}} \times \left(1 - \frac{1}{L} + \text{MMR}\right)$$
   $$\text{Short Liquidation} = P_{\text{entry}} \times \left(1 + \frac{1}{L} - \text{MMR}\right)$$
4. Aggregate cumulative volume into price brackets or "bins" (e.g. 50 USD) to identify where major liquidity pools concentrate.

---

### 2. How to Use the Application (Super Easy Mode)

#### Option A: 1-Click Launch (Recommended for Windows)
In the project root folder, simply **double-click the file:**
👉 **`start_dashboard.bat`**

This script will start the local server and **automatically open your web browser** at:
🔗 **`http://localhost:8000/`**

#### Option B: Launch from Terminal
```powershell
# Start the FastAPI server
py -3.12 -m uvicorn liqscope.api.app:create_app --factory --host 0.0.0.0 --port 8000
```
Then open your browser at [http://localhost:8000](http://localhost:8000).

---

### 3. Visual Panel Features ("Terminal Heat" Design System)

Upon opening [http://localhost:8000](http://localhost:8000), you will access the interactive institutional telemetry panel:

1. **Automatic 2-Minute Auto-Refresh (120 s):**
   * Automatically polls Binance every **120 seconds** in the background with live countdown (`Auto: 02:00 -> 01:59...`) and sync timestamp.
   * Instant manual refresh button available at any time.
2. **100% Live Binance Long/Short Account Telemetry:**
   * Directly connected to `globalLongShortAccountRatio`, breaking artificial 50/50 symmetry and weighting liquidation pools with real exchange statistics (e.g. 77.9% Long / 22.1% Short).
3. **CoinGlass-Style Hotspots & Dominant Leverage Tags:**
   * 🔥 **`MAX LIQ` Badge:** Glowing amber highlight on the primary liquidation cluster.
   * **Dominant Leverage Badges:** Explicit labels (`[25x]`, `[50x]`, `[100x]`) for each price ladder row.
   * **Interactive Cluster Inspector:** Click any ladder row or the epicenter card to inspect Tier MMR, Delta to Mark, USD volume, and Cascade Risk.
   * **Dynamic Optimal Bins:** Automatically selects `10 USD` for ETHUSDT and `50 USD` for BTCUSDT.
4. **Multi-Tab Institutional Navigation:**
   * 🔥 **Heatmap Telemetry:** Proportional depth ladder, risk bento tiles, and magnetic attraction zone.
   * 📊 **Model & Data:** Cryptographic transparency protocol and verified formula documentation.
   * 📐 **MMR Tiers & Simulator:** Interactive calculator with "Use Current Mark" button and Binance tier brackets.
   * 🔔 **Alerts & Telemetry Radar:** Real-time liquidation wall and cascade risk monitor.
   * 📖 **User Manual:** Complete guide embedded directly in the dashboard, at [`MANUAL.md`](MANUAL.md), and at [`/manual`](http://localhost:8000/manual).

---

### 4. Configuration (`.env`)

LiqScope uses `pydantic-settings` for robust, type-safe configuration. Copy `.env.example` to `.env` in the root folder:

```bash
cp .env.example .env
```

| Variable | Description | Default | Valid Options |
| :--- | :--- | :--- | :--- |
| `LIQSCOPE_ENV` | Runtime environment | `development` | `development`, `production`, `test`, `demo` |
| `BINANCE_FUTURES_BASE_URL` | Binance Futures API Base URL | `https://fapi.binance.com` | Official REST URL or mock |
| `SERVER_HOST` | HTTP server host binding | `0.0.0.0` | Local IP or `127.0.0.1` |
| `SERVER_PORT` | Listening port | `8000` | Integer (e.g. `8000`, `8080`) |
| `LIQSCOPE_CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:5173", "http://127.0.0.1:5173"]` | JSON list of explicit domains |
| `STORAGE_BACKEND` | Storage engine | `sqlite` | `sqlite`, `postgres` |
| `DATABASE_PATH` | SQLite database file path | `liqscope.db` | Local file path |

> [!NOTE]
> **No API keys or secrets are required** to fetch live Binance data. LiqScope exclusively queries Binance Futures public market data endpoints.

---

### 5. REST API Endpoints

In addition to the visual dashboard, LiqScope provides a complete canonical versioned REST API:

* **Web Visualizer:** `GET /` (Interactive visual dashboard).
* **User Manual:** `GET /manual` or [`MANUAL.md`](MANUAL.md) (Complete telemetry and usage manual).
* **Supported Symbols & Recommended Bins:** `GET /api/v1/symbols` (Returns supported symbols and their `default_bin_size`).
* **Liquidation Heatmap:** `GET /api/v1/heatmap/{symbol}`
  * Query parameters:
    * `min_price`: Lower price boundary (float).
    * `max_price`: Upper price boundary (float).
    * `bin_size`: Price bin step in USD (e.g. `10.0` for ETH, `50.0` for BTC).
    * `ratio_mode`: `'live'` (Binance live account ratio) or `'neutral'` (static 50/50).
    * `assumed_long_ratio`: Custom ratio (0.0 to 1.0) with precedence over `ratio_mode`.
    * `source`: `'live'` (Binance) or `'demo'` (synthetic).
  * Extended response fields:
    * `dominant_leverage` & `leverages`: Leverage distribution breakdown for each bin.
    * `long_account_ratio` & `short_account_ratio`: Live Binance account telemetry.
    * `cached` & `data_age_sec`: TTL cache status and data age.
* **Service Health:** `GET /health` (Status `{"status": "ok", "env": "..."}`).
* **Interactive Documentation (Swagger UI):** `GET /docs`
* **ReDoc Specification:** `GET /redoc`

---

### 6. Installation & Development Environment

#### Prerequisites
- **Python 3.12+** installed.
- **Git** installed.

#### Virtual Environment Setup
```powershell
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies in editable mode with development tools
pip install -e .[dev]
```

#### Quality Verification & Tests (100% Coverage)
```powershell
# 1. Formatting and code linting (Ruff)
py -3.12 -m ruff check src tests
py -3.12 -m ruff format --check src tests

# 2. Strict static type checking (Mypy)
py -3.12 -m mypy src tests

# 3. Complete test suite with coverage report (140 tests)
py -3.12 -m pytest --cov=liqscope --cov-report=term-missing
```

---

### 7. Codebase Structure

```text
src/liqscope/
├── api/                  # FastAPI app, REST routes, and interactive HTML dashboard
│   ├── app.py            # FastAPI factory and middleware setup
│   ├── dashboard.py      # Terminal Heat dashboard template with 2-min auto-refresh
│   └── routes/heatmap.py # Analytical endpoint GET /api/v1/heatmap/{symbol}
├── connectors/           # Data connectors (Binance Futures REST & WebSockets)
│   ├── binance_rest.py   # aiohttp client for fapi.binance.com
│   └── base.py           # DataSource abstract protocols
├── engine/               # Financial modeling and liquidation mathematics
│   ├── formulas.py       # Liquidation formulas (Long/Short) and MMR logic
│   ├── tiers.py          # Leverage brackets (5x to 100x)
│   └── aggregator.py     # Price binning and coverage calculation
├── models/               # Validated Pydantic v2 domain models
├── storage/              # SQLite / PostgreSQL decoupled repository layer
└── config.py             # Centralized settings via pydantic-settings
```
