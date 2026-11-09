# LiqScope — Institutional Crypto Liquidation Terminal & Derivatives Suite

<p align="center">
  <img src="https://img.shields.io/badge/LiqScope-Institutional%20Terminal-00f090?style=for-the-badge&logo=curseforge&logoColor=black" alt="LiqScope Terminal" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/TradingView-Lightweight%20Charts-2962FF?style=for-the-badge&logo=tradingview&logoColor=white" alt="TradingView" />
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/License-MIT-ffd700?style=for-the-badge" alt="License" />
</p>

<p align="center">
  <a href="#-español"><b>🇪🇸 Versión en Español</b></a> &nbsp;|&nbsp; 
  <a href="#-english"><b>🇬🇧 English Version</b></a>
</p>

---

# 🇪🇸 Español

## LiqScope — Terminal Institucional de Derivados y Mapas de Calor de Liquidaciones

> [!IMPORTANT]
> **Aviso de Responsabilidad:** Herramienta analítica cuantitativa de código abierto para fines educativos e informativos. No constituye asesoramiento financiero ni recomendación comercial. LiqScope **NO** custodia fondos, **NO** ejecuta órdenes ni solicita credenciales privadas con permisos de trading.

**LiqScope** es una estación de trabajo analítica de alto rendimiento para derivados cripto. Conecta de forma directa y sin intermediarios con los servidores públicos de **Binance Futures USDⓈ-M**, **Bybit Linear** y registros oficiales de la **SEC**, ofreciendo mapas de calor de liquidación continuos, gráficos interactivos de TradingView, matriz de financiación multi-exchange, escáner de más de 620 contratos con radar de ballenas, tracker institucional de ETFs Spot y notificaciones en tiempo real vía Telegram y WebSockets.

---

### 1. Módulos y Capacidades del Sistema

```mermaid
graph TD
    subgraph Fuentes de Datos Oficiales
        BIN["Binance Futures USDⓈ-M (Mark, OI, Ratio L/S, Klines)"]
        BYB["Bybit Linear (Tickers, Funding Rates)"]
        SEC["SEC 13F / Custodia Institucional (ETFs Spot)"]
    end

    subgraph Motores Backend LiqScope
        ENG1["Motor de Liquidaciones MMR (Tiers 1-10+)"]
        ENG2["Agregador de 6 Horizontes (12h, 24h, 3d, 1w, 1m, 3m)"]
        ENG3["Funding Matrix Engine (Cross-Exchange APR)"]
        ENG4["Screener & Whale Radar (620+ Pares, OI Surge)"]
        ENG5["ETF Tracker Service (10 BTC / 8 ETH Funds)"]
        ENG6["Telegram Bot & WebSocket Feeder"]
    end

    subgraph Interfaz Institucional (Terminal Heat)
        UI1["TradingView Lightweight Charts (Velas + Sub-paneles)"]
        UI2["Lienzo Canvas 2D (Capas Térmicas LiqScope Turbo)"]
        UI3["Escalera DOM de Profundidad de Liquidaciones"]
        UI4["Bento Tiles de Riesgo & Barómetro de Amplitud"]
    end

    BIN & BYB & SEC --> ENG1 & ENG2 & ENG3 & ENG4 & ENG5 & ENG6
    ENG1 & ENG2 & ENG3 & ENG4 & ENG5 & ENG6 --> UI1 & UI2 & UI3 & UI4
```

#### 1.1. Mapa de Calor de Liquidaciones (LiqScope Heat & Turbo)
* **Lienzo Gráfico TradingView (Lightweight Charts v4.2):** Velas de alta resolución (OHLCV) con paneo, zoom interactivo y sincronización automática.
* **Capas Térmicas Canvas 2D Continuas:** Proyección de franjas de calor horizontales semi-transparentes sobre el gráfico de velas.
* **Paletas Cromáticas Profesionales:**
  * 🔥 **LiqScope Turbo (Por defecto):** Gradiente térmico continuo de 4 paradas (Azul Marino Profundo $\rightarrow$ Cian $\rightarrow$ Verde Esmeralda $\rightarrow$ Amarillo Neón).
  * 🟢🔴 **Longs / Shorts:** Verde esmeralda para Long Pools y Rojo rubí para Short Pools.
  * ⚡ **Plasma Neón:** Gradiente violeta magenta neón para pantallas OLED de alto contraste.
* **Epicentro de Máxima Liquidación (🎯 `MAX LIQ`):** Destaque con línea discontinua dorada ámbar y resplandor pulsante en el clúster con mayor liquidez acumulada del libro.
* **Selector de Intensidad Térmica:** Multiplicador dinámico de contraste (`1.0x`, `1.5x`, `2.0x`, `2.5x`).

#### 1.2. Selector de 6 Horizontes Temporales de Acumulación
* Permite alternar la ventana de acumulación entre: **`⏱️ 12h`**, **`⏱️ 24h`**, **`⏱️ 3d`**, **`⏱️ 1w`**, **`⏱️ 1m`** y **`⏱️ 3m`**.
* **Fundamento Cuantitativo:** A corto plazo (12h/24h) predominan posiciones intradía con alto apalancamiento (50x–100x) muy cercanas al precio actual. En marcos amplios (1m/3m) se acumulan posiciones de swing trading institucional con apalancamientos moderados (5x–10x) y zonas de liquidación más alejadas.

#### 1.3. Súper Gráficos (Velas + Sub-paneles Sincronizados)
* **Sub-panel de Interés Abierto (Open Interest):** Oscilador en tiempo real que muestra la expansión o contracción del capital apalancado en contratos.
* **Sub-panel de Histórico de Tasas de Financiación:** Histograma con barras bicolores (verde cuando los longs pagan a los shorts, rojo cuando los shorts pagan a los longs).
* **Sincronización Total:** Ambos sub-paneles se desplazan y escalan en conjunto con la escala temporal del gráfico principal de velas.

#### 1.4. Matriz Térmica Multi-Exchange de Tasas de Financiación
* Comparativa en vivo entre **Binance Futures** y **Bybit Linear**.
* Cálculo de **Tasa Promedio** y **APR Anualizado**.
* **Temporizador Regresivo:** Cuenta atrás exacta para la siguiente liquidación de financiación (ej. cada 8 horas).
* **Detección de Sobrecalentamiento (*Overheat*):** Alertas visuales automáticas cuando el mercado presenta apalancamiento excesivo al alza o a la baja.

#### 1.5. Screener de Mercado y Radar de Ballenas (620+ Pares)
* Escaneo paralelo de más de **620 contratos perpetuos** en tiempo real.
* **Barómetro de Amplitud de Mercado:** Porcentaje y recuento en vivo de contratos alcistas (*Advancers*) versus bajistas (*Decliners*).
* **Radar de Ballenas (OI Surge):** Algoritmo que detecta picos anómalos de acumulación de Open Interest respecto al volumen diario:
  * 🐋 **Acumulación Institucional:** Fuerte subida de precio con entrada masiva de posiciones largas.
  * 🐋 **Distribución Institucional:** Fuerte caída de precio con apertura agresiva de posiciones cortas.
  * ⚡ **Squeeze Risk:** Ratio de apalancamiento extremo con alta probabilidad de barrida inminente.
* **Botón de Análisis Instantáneo:** Al hacer clic en `🔍 Analizar`, carga el par automáticamente en el Heatmap y en el gráfico de TradingView.

#### 1.6. Tracker Institucional de ETFs Spot (Bitcoin & Ethereum)
* **10 Fondos de Bitcoin:** BlackRock (`IBIT`), Fidelity (`FBTC`), ARK 21Shares (`ARKB`), Bitwise (`BITB`), Grayscale (`GBTC`), Grayscale Mini (`BTC`), VanEck (`HODL`), Valkyrie (`BRRR`), Invesco Galaxy (`BTCO`), Franklin Templeton (`EZBC`).
* **8 Fondos de Ethereum:** BlackRock (`ETHA`), Fidelity (`FETH`), Grayscale (`ETHE`), Grayscale Mini (`ETH`), Bitwise (`ETHW`), 21Shares (`CETH`), Franklin Templeton (`EZET`), Invesco Galaxy (`QETH`).
* **Métricas Oficiales:** AUM agregado en USD, monedas físicas bajo custodia, flujo neto de la última sesión e inflow acumulado histórico.
* **Gráfico de Barras de Flujos Netos Diarios:** Visualización de las últimas 14 sesiones bursátiles con tooltips del fondo líder.
* **Detalle por Custodio Auditado:** Información de custodia (*Coinbase Prime, Fidelity Digital Assets, Gemini Trust*) y comisión anual de gestión (*Expense Ratio*).

#### 1.7. Bot de Telegram y Streaming WebSockets
* Notificaciones instantáneas al canal o chat privado configurado ante eventos de liquidación y cruces de muros clave.
* Comandos interactivos `/status`, `/heatmap BTCUSDT`, etc.
* Conexión WebSocket nativa de baja latencia en `/ws/liquidations`.

---

### 2. Inicio Rápido y Despliegue

#### Opción A: Despliegue con Docker (Recomendado en Producción)
```bash
# Clonar el repositorio
git clone https://github.com/jsoto-06/LiqScope.git
cd LiqScope

# Construir e iniciar el contenedor en segundo plano
docker compose up -d --build
```
Abre tu navegador en: **`http://localhost:8000`**

#### Opción B: Inicio en 1 Clic en Windows
En la carpeta raíz del proyecto, haz doble clic en:
👉 **`start_dashboard.bat`** (Inicia el servidor y abre el navegador automáticamente).

#### Opción C: Inicio desde Terminal Local (Python 3.12+)
```bash
# Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -e .

# Iniciar el servidor ASGI
uvicorn liqscope.api.app:create_app --factory --host 0.0.0.0 --port 8000
```

---

### 3. Configuración del Sistema (`.env`)

Copia la plantilla de configuración:
```bash
cp .env.example .env
```

| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `LIQSCOPE_ENV` | Entorno de ejecución (`production`, `development`, `demo`, `test`) | `development` |
| `SERVER_HOST` | Dirección de escucha de la interfaz HTTP | `0.0.0.0` |
| `SERVER_PORT` | Puerto de escucha de la aplicación | `8000` |
| `BINANCE_FUTURES_BASE_URL` | URL de la API de producción de Binance Futures | `https://fapi.binance.com` |
| `TELEGRAM_BOT_TOKEN` | Token de BotFather para alertas de Telegram | *(Opcional)* |
| `TELEGRAM_CHAT_ID` | Identificador de chat o canal de Telegram | *(Opcional)* |
| `STORAGE_BACKEND` | Motor de almacenamiento persistente | `sqlite` |
| `DATABASE_PATH` | Ruta del archivo de base de datos local | `liqscope.db` |

---

### 4. Endpoints de la API REST (`/api/v1`)

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Chequeo de estado del servicio y entorno activo |
| `GET` | `/api/v1/heatmap/{symbol}` | Mapa de calor con bins de liquidación, MMR y 6 horizontes (`?timeframe=24h&bin_size=50`) |
| `GET` | `/api/v1/symbols` | Listado de pares soportados con granularidad recomendada |
| `GET` | `/api/v1/klines/{symbol}` | Velas históricas OHLCV (`?interval=1h&limit=100`) |
| `GET` | `/api/v1/klines/{symbol}/open-interest` | Historial de Open Interest sincronizado |
| `GET` | `/api/v1/klines/{symbol}/funding-rate` | Historial de tasas de financiación |
| `GET` | `/api/v1/funding` | Matriz multi-exchange de tasas de financiación, APR y tiempo restante |
| `GET` | `/api/v1/screener` | Screener de 620+ contratos con amplitud de mercado y radar de ballenas |
| `GET` | `/api/v1/etfs` | Tracker de ETFs Spot (Bitcoin y Ethereum) con flujos diarios y AUM |
| `GET` | `/api/v1/alerts` | Monitor de alertas y muros de liquidación activos |
| `WS` | `/ws/liquidations` | Canal WebSocket en vivo para eventos de liquidación forzada |

---

# 🇬🇧 English Version

## LiqScope — Institutional Crypto Liquidation Terminal & Derivatives Suite

> [!IMPORTANT]
> **Disclaimer:** Open-source quantitative research tool for educational and informational purposes only. Not financial or trading advice. LiqScope does **NOT** custody funds, does **NOT** place orders, and does **NOT** require API keys with trading permissions.

**LiqScope** is a high-performance analytics workstation for cryptocurrency derivatives. Connected directly to official public endpoints from **Binance Futures USDⓈ-M**, **Bybit Linear**, and **SEC** institutional filings, it delivers continuous liquidation heatmaps, interactive TradingView charts, multi-exchange funding matrices, a 620+ pair market screener with whale accumulation radar, a Spot ETF tracker, and real-time Telegram / WebSocket telemetry.

---

### Key Capabilities

1. **TradingView Lightweight Charts (v4.2.0) + Canvas 2D Heatmap Layers:**
   - Multi-resolution interactive candlestick charting with smooth pan and zoom.
   - Semi-transparent continuous liquidation bands projected over candles.
   - 3 Pro Color Palettes: `🔥 LiqScope Turbo` (default), `🟢🔴 Longs/Shorts`, and `⚡ Plasma Neon`.
   - `MAX LIQ` epicenter indicator with animated golden aura.
2. **6 Accumulation Lookback Horizons:**
   - Switch effortlessly between `12h`, `24h`, `3d`, `1w`, `1m`, and `3m`.
   - Mathematically models how high-leverage scalpers (50x-100x) dominate short timeframes while swing institutional trades (5x-10x) anchor macro horizons.
3. **Super Charts with Synchronized Sub-Panels:**
   - Real-time Open Interest oscillator.
   - Historical Funding Rates histogram with positive/negative color coding.
   - Time scales strictly synced to candlestick movements.
4. **Cross-Exchange Funding Rates Matrix:**
   - Live comparison between Binance Futures and Bybit Linear.
   - Real-time Annualized APR, next funding countdown, and thermal overheat detection.
5. **Derivatives Screener & Whale Radar (620+ Contracts):**
   - Live Market Breadth Barometer (Advancers vs Decliners count and percentages).
   - OI Surge anomaly detection (Whale Accumulation, Distribution, Squeeze Risk).
   - 1-Click `🔍 Analyze` action opening the pair instantly inside the Heatmap.
6. **Spot Bitcoin & Ethereum ETF Tracker:**
   - Comprehensive tracking of 10 Bitcoin Spot ETFs (IBIT, FBTC, ARKB...) and 8 Ethereum Spot ETFs (ETHA, FETH...).
   - AUM, physical coins under custody, daily net flows, historical cumulative inflows, and custodian auditing.
7. **Telegram Bot & WebSockets:**
   - Automated alerts on liquidation wall sweeps and interactive status commands.
   - Native streaming at `/ws/liquidations`.

---

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/jsoto-06/LiqScope.git
cd LiqScope

# Build and run with Docker Compose
docker compose up -d --build
```
Access the terminal at: **`http://localhost:8000`**

---

### License
Released under the **MIT License**. Built for transparency, quantitative research, and institutional execution.
