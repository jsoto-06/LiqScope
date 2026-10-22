# LiqScope — Mapa de Liquidaciones para Cripto

> [!IMPORTANT]
> **Aviso:** Estimaciones con fines informativos. No es asesoramiento financiero ni señal de trading.

LiqScope es una herramienta analítica de solo lectura y visualización en tiempo real de zonas de liquidación apalancada por nivel de precio para BTC y principales altcoins.

**LiqScope:**
- **NO** ejecuta órdenes.
- **NO** gestiona fondos.
- **NO** emite señales de compra o venta.
- Todo dato proyectado en el mapa se cataloga y etiqueta explícitamente como **ESTIMACIÓN**.

---

## 1. Arquitectura del Proyecto

```text
src/liqscope/
├── config.py             # Configuración centralizada vía pydantic-settings
├── logging_config.py     # Logging estructurado en formato JSON sin secretos
├── models/               # Modelos de datos Pydantic v2 (Trade, Liquidation, Heatmap, etc.)
├── connectors/           # Adaptadores por exchange bajo interfaz común DataSource (aiohttp)
├── engine/               # Fórmulas de liquidación, escalones de margen y agregación en bins
├── storage/              # Capa de persistencia desacoplada (SQLite / PostgreSQL)
├── api/                  # Endpoints REST y servidor WebSocket con FastAPI
└── demo/                 # Cargador y generador de datos sintéticos de demostración
```

---

## 2. Stack Tecnológico y Licencias

- **Backend:** Python 3.12, FastAPI, Pydantic v2 (`pydantic-settings`).
- **Red y WebSockets:** `aiohttp` unificado para llamadas REST asíncronas y streams WebSocket persistentes.
- **Persistencia:** SQLite para desarrollo local con capa de repositorio desacoplada preparada para migración transparente a PostgreSQL / TimescaleDB.
- **Calidad de Código y Seguridad:**
  - `ruff` (linter y formateador ultrarrápido).
  - `mypy` (chequeo estricto de tipos estáticos).
  - `gitleaks` (escaneo preventivo de secretos y tokens en CI y pre-commit).
  - `pytest` & `pytest-cov` (cobertura unitaria e integración con umbral mínimo del 80%).
- **Frontend (Fase 5):** React, Vite, TypeScript.
  - **Lightweight Charts:** Gráfica de velas de alta eficiencia ([Licencia Apache 2.0](https://github.com/tradingview/lightweight-charts/blob/master/LICENSE)).
  - **Plotly.js:** Visualización de mapa de calor / heatmap ([Licencia MIT](https://github.com/plotly/plotly.js/blob/master/LICENSE)).

---

## 3. Modo Demo / Offline

Para garantizar reproducibilidad sin necesidad de credenciales ni conexión a internet activa, LiqScope cuenta con un modo demo que lee fixtures locales sintéticos (`fixtures/demo/`).

Todos los datos contenidos en `fixtures/demo/` están explícitamente marcados con el flag `_synthetic: true` y no representan órdenes de mercado reales ni cuentas reales.

Para iniciar en modo demo:
```bash
# Configurar en .env
LIQSCOPE_ENV=demo
```

---

## 4. Instalación y Uso

### Requisitos previos
- Python 3.12+
- Git

### Instalación en entorno local
```bash
# 1. Clonar el repositorio
git clone <repo-url>
cd LiqScope

# 2. Crear entorno virtual
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

# 3. Instalar dependencias en modo editable con herramientas de desarrollo
pip install -e .[dev]

# 4. Configurar variables de entorno
cp .env.example .env
```

### Ejecución de comprobaciones de calidad (Fase 0)
```bash
# Formateo y linting
ruff check .
ruff format --check .

# Verificación de tipos estricta
mypy src tests

# Ejecución de tests con reporte de cobertura
pytest --cov=liqscope --cov-report=term-missing
```
