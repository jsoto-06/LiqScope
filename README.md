# LiqScope — Mapa de Calor de Liquidaciones Cripto

> [!IMPORTANT]
> **Aviso de Responsabilidad:** Herramienta analítica de solo lectura con fines educativos e informativos. No constituye asesoramiento financiero ni señales de compra o venta. LiqScope **NO** gestiona fondos, **NO** ejecuta órdenes ni solicita claves privadas o API keys con permisos de trading.

---

## 1. Confirmación de Origen y Realidad de los Datos

Una de las dudas más frecuentes en los mapas de calor de liquidaciones es si la información proyectada es **real**:

### ¿Qué datos son 100 % REALES en vivo?
* **Precio Mark (`mark_price`) en tiempo real:** Obtenido directamente de los servidores de producción de **Binance Futures USDⓈ-M** (`fapi.binance.com/fapi/v1/premiumIndex`).
* **Interés Abierto (`total_open_interest_usd`):** Volumen global real de contratos de futuros abiertos en el exchange en este instante (`fapi.binance.com/fapi/v1/openInterest`). Actualmente representa miles de millones de dólares (ej. ~95.000 BTC o ~$7.700M USD).
* **Parámetros Oficiales de Margen (MMR):** Escalones de margen de mantenimiento basados en la normativa oficial de apalancamiento de Binance.

### ¿Por qué las zonas de liquidación son un MODELO analítico?
Ningún exchange de criptoderivados del mundo (Binance, Bybit, OKX, etc.) publica las posiciones individuales ni los precios de entrada de cada usuario por secreto bancario y protección de la privacidad de sus clientes.

Por ello, plataformas profesionales como LiqScope, Coinglass o Kingfisher utilizan **modelos analíticos matemáticos**:
1. Toman el **Open Interest 100 % real** del mercado.
2. Lo distribuyen en los tramos de apalancamiento habituales del mercado (5x, 10x, 25x, 50x y 100x).
3. Aplican las fórmulas exactas de liquidación forzada de Binance:
   $$\text{Liquidación Long} = P_{\text{entrada}} \times \left(1 - \frac{1}{L} + \text{MMR}\right)$$
   $$\text{Liquidación Short} = P_{\text{entrada}} \times \left(1 + \frac{1}{L} - \text{MMR}\right)$$
4. Agrupan el volumen acumulado en escalones o "bins" de precio (ej. 50 USD) para identificar dónde se concentran las mayores bolsas de liquidez.

---

## 2. Cómo Usar la Aplicación (Modo Súper Fácil)

### Opción A: Inicio en 1 Clic (Recomendado en Windows)
En la carpeta raíz del proyecto, simplemente haz **doble clic en el archivo:**
👉 **`start_dashboard.bat`**

Este script ejecutará el servidor local y **abrirá automáticamente tu navegador web** en:
🔗 **`http://localhost:8000/`**

### Opción B: Inicio desde la Terminal
```powershell
# Iniciar el servidor FastAPI
py -3.12 -m uvicorn liqscope.api.app:create_app --factory --host 0.0.0.0 --port 8000
```
Luego abre tu navegador en [http://localhost:8000](http://localhost:8000).

---

## 3. Funcionalidades del Panel Visual

Al abrir [http://localhost:8000](http://localhost:8000), tendrás acceso al panel gráfico interactivo:

1. **Auto-actualización cada 2 minutos:**
   - La aplicación consulta a Binance cada **120 segundos** de forma automática en segundo plano.
   - Cuenta con una etiqueta con cuenta regresiva visible (`Auto: 02:00 -> 01:59...`) y muestra la hora exacta de la última sincronización (`Sinc: HH:MM:SS`).
   - Puedes forzar una actualización manual instantánea en cualquier momento pulsando el botón **"Actualizar"**.
2. **Selector de Pares:**
   - Cambia entre **BTCUSDT** y **ETHUSDT** con 1 solo clic.
3. **Modo Live vs. Demo:**
   - **Live (Binance):** Datos de mercado en vivo desde la API de Binance Futures.
   - **Demo:** Datos sintéticos locales para pruebas sin conexión o desarrollo offline.
4. **Filtros de Rango y Granularidad:**
   - Configura el **Precio Mínimo** y **Precio Máximo** para estudiar una franja concreta.
   - Cambia el tamaño del bin (**50 USD, 100 USD, 250 USD o 500 USD**).
5. **Escalera de Liquidaciones:**
   - **Barras Rojas (Shorts):** Zonas de liquidación por encima del precio actual.
   - **Línea Púrpura Centrada:** Precio Mark actual de mercado.
   - **Barras Verdes (Longs):** Zonas de liquidación por debajo del precio actual.

---

## 4. Configuración (`.env`)

LiqScope utiliza `pydantic-settings` para la gestión segura de configuración. Para personalizar parámetros, crea un archivo `.env` en la raíz copiando `.env.example`:

```bash
cp .env.example .env
```

### Variables disponibles:

| Variable | Descripción | Valor por defecto | Opciones válidas |
| :--- | :--- | :--- | :--- |
| `LIQSCOPE_ENV` | Entorno de ejecución | `development` | `development`, `production`, `test`, `demo` |
| `BINANCE_FUTURES_BASE_URL` | URL de la API de Binance Futures | `https://fapi.binance.com` | URL REST oficial o mock |
| `SERVER_HOST` | Host para el servidor HTTP | `0.0.0.0` | IP local o `127.0.0.1` |
| `SERVER_PORT` | Puerto de escucha | `8000` | Entero (ej. `8000`, `8080`) |
| `CORS_ORIGINS` | Orígenes permitidos (CORS) | `["*"]` | Lista JSON de dominios |
| `STORAGE_BACKEND` | Base de datos | `sqlite` | `sqlite`, `postgres` |
| `DATABASE_PATH` | Ruta de base de datos SQLite | `liqscope.db` | Ruta a archivo local |

> [!NOTE]
> Para consultar datos en vivo de Binance **no se necesitan claves de API** (`API Key` ni `API Secret`). LiqScope únicamente utiliza los endpoints públicos de mercado de Binance Futures.

---

## 5. Endpoints de la API REST

Además del panel visual, LiqScope expone una API REST para integración analítica:

* **Visualizador Web:** `GET /` (Dashboard visual interactivo).
* **Mapa de Calor:** `GET /api/v1/heatmap/{symbol}`
  * Parámetros opcionales:
    * `min_price`: Límite inferior de precio (float).
    * `max_price`: Límite superior de precio (float).
    * `bin_size`: Tamaño del escalón en USD (defecto: `50.0`).
    * `assumed_long_ratio`: Proporción de Longs estimada (defecto: `0.5`).
    * `source`: `live` (Binance) o `demo` (sintético).
* **Salud del Servidor:** `GET /health` (Estado `{"status": "ok", "env": "..."}`).
* **Documentación Interactiva (Swagger UI):** `GET /docs`
* **Especificación ReDoc:** `GET /redoc`

---

## 6. Instalación y Entorno de Desarrollo

### Requisitos previos
- **Python 3.12+** instalado.
- **Git** instalado.

### Configuración del entorno virtual
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

### Comprobaciones de Calidad y Tests (100 % Cobertura)
```powershell
# 1. Formateo y linter de código (Ruff)
py -3.12 -m ruff check src tests
py -3.12 -m ruff format --check src tests

# 2. Tipado estricto (Mypy)
py -3.12 -m mypy src tests

# 3. Suite completa de tests con reporte de cobertura
py -3.12 -m pytest --cov=liqscope --cov-report=term-missing
```

---

## 7. Estructura del Código

```text
src/liqscope/
├── api/                  # FastAPI app, rutas REST y dashboard visual interactivo
│   ├── app.py            # Fábrica FastAPI y middlewares
│   ├── dashboard.py      # Plantilla HTML con auto-refresco de 2 min
│   └── routes/heatmap.py # Endpoint analítico GET /api/v1/heatmap/{symbol}
├── connectors/           # Conectores de datos (Binance Futures REST y WebSockets)
│   ├── binance_rest.py   # Cliente aiohttp para fapi.binance.com
│   └── base.py           # Protocolos base de DataSource
├── engine/               # Modelado financiero y matemáticas de liquidación
│   ├── formulas.py       # Fórmulas de liquidación (Long/Short) y MMR
│   ├── tiers.py          # Escalones de apalancamiento (5x a 100x)
│   └── aggregator.py     # Agregación en bins de precio y cálculo de cobertura
├── models/               # Modelos de datos validados con Pydantic v2
├── storage/              # Capa de almacenamiento SQLite / PostgreSQL
└── config.py             # Configuración desacoplada vía pydantic-settings
```
