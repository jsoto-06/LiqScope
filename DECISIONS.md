# Architecture Decision Records (ADR) — LiqScope

Este documento registra cada decisión técnica clave, su contexto, alternativas evaluadas y justificación de acuerdo con los requisitos del proyecto.

---

## ADR-001: Estructura del Proyecto y Empaquetado `src/liqscope`
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Se requiere una arquitectura modular, extensible y testeable que separe claramente la ingesta, el cálculo, la persistencia, la API y la interfaz web.
- **Decisión:** Adoptar el layout estándar `src/liqscope/` con submódulos independientes (`connectors`, `engine`, `models`, `storage`, `api`, `demo`).
- **Consecuencias:** Evita colisiones de importación con módulos locales en tests y asegura que los imports utilicen la ruta canónica `liqscope.<submodulo>`.

---

## ADR-002: Elección de Librería Unificada para HTTP y WebSockets (`aiohttp`)
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Se requiere consultar APIs REST (respaldo y datos iniciales) y mantener streams continuos de WebSockets (trades, forceOrder, orderbook, open interest). Utilizar múltiples librerías (por ejemplo, `httpx` para REST y `websockets` para WS) fragmenta la configuración de SSL/TLS, pool de sockets y manejo de timeouts.
- **Opciones evaluadas:**
  1. *`httpx` + `websockets`:* `httpx` es excelente para REST pero no incluye cliente WebSocket nativo maduro de alto rendimiento sin extensiones de terceros.
  2. *`aiohttp`:* Provee cliente HTTP asíncrono (`ClientSession`) y cliente WebSocket nativo (`ClientSession.ws_connect`) en un único paquete altamente probado y optimizado.
  3. *`ccxt.pro`:* Requiere suscripciones comerciales para ciertas funciones avanzadas y añade capas de abstracción no siempre compatibles con la granularidad necesaria para streams raw de liquidaciones.
- **Decisión:** Adoptar **`aiohttp`** como la única librería para todas las llamadas HTTP y conexiones WebSocket del backend.
- **Consecuencias:** Unifica el ciclo de vida de sesiones de red, pooling de conexiones TCP, configuración de proxys y gestión de timeouts bajo un único motor.

---

## ADR-003: Licencias de Librerías de Visualización Frontend
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** El frontend requiere visualizar tanto un gráfico de precios temporal interactivo como un mapa de calor (heatmap) 2D con niveles de liquidación agregados. Se debe asegurar que las librerías utilicen licencias de código abierto comerciales y permisivas.
- **Decisión:**
  1. **TradingView Lightweight Charts:**
     - **Licencia:** [Apache License 2.0](https://github.com/tradingview/lightweight-charts/blob/master/LICENSE).
     - **Justificación:** Es una librería open source permisiva que permite uso comercial y privado sin costos de licencia ni necesidad de divulgar código privativo. Proporciona rendimiento de renderizado por canvas de 60 FPS ideal para gráficos de velas financieras.
  2. **Plotly.js (vía React-Plotly.js):**
     - **Licencia:** [MIT License](https://github.com/plotly/plotly.js/blob/master/LICENSE).
     - **Justificación:** Permite renderizar heatmaps y gráficos matriciales interactivos sin restricciones comerciales. En caso de requerir un rendimiento superior en Fase 5, se complementará con un canvas propio en WebGL/HTML5 2D sin cambiar la compatibilidad de licencias.

---

## ADR-004: Versionado de Python y Lockfile Reproducible
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Se debe garantizar la reproducibilidad de los entornos de ejecución en máquinas de desarrollo y en integración continua (CI).
- **Decisión:**
  1. Fijar `.python-version` en `3.12`.
  2. Mantener `pyproject.toml` para especificación declarativa de dependencias con rangos compatibles.
  3. Proporcionar `requirements.lock` con el congelado exacto de versiones resueltas para builds deterministas.

---

## ADR-005: Seguridad y Prevención de Fugas de Secretos con Gitleaks
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** LiqScope consume APIs públicas pero puede interactuar con endpoints que requieran claves en fases avanzadas. Nunca debe filtrarse ninguna clave, credencial o variable confidencial al repositorio.
- **Decisión:** Integrar `gitleaks` de forma obligatoria en:
  1. `.pre-commit-config.yaml` para bloqueo local antes del commit.
  2. `.github/workflows/ci.yml` para validación automática en cada pull request y push.
  3. Archivo `.env.example` sanitizado sin valores reales, con exclusión obligatoria de `.env` en `.gitignore`.

---

## ADR-006: Validación Estricta de Configuración con Pydantic Settings
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Valores inválidos en variables de entorno (como puertos negativos, niveles de logging desconocidos o umbrales de reconexión absurdos) pueden provocar comportamientos erráticos en tiempo de ejecución.
- **Decisión:** Implementar validación en `pydantic-settings` con validadores de campo que rechacen explícitamente puertos fuera de `1..65535`, niveles de log no reconocidos y valores temporales negativos, lanzando excepciones `ValidationError` claras en el inicio.

---

## ADR-007: Persistencia Desacoplada (Repository Pattern)
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Se requiere SQLite para desarrollo rápido y pruebas sin dependencias de servicios externos pesados, pero el sistema debe poder migrar a PostgreSQL o TimescaleDB en entornos productivos.
- **Decisión:** Diseñar una interfaz abstracta de almacenamiento (`BaseStorageRepository`) que defina métodos asíncronos (`save_snapshot`, `get_latest_snapshot`, `record_liquidation`). El código del motor y de la API solo interactuará con dicha interfaz.

---

## ADR-008: Módulo de Carga Sintética Offline (`demo/loader.py`) y Auditoría de Estructura
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Para desarrollo local, pruebas unitarias y modo demo sin dependencias externas, se requiere leer fixtures sintéticos de forma tipada, segura y controlada.
- **Decisión:** Implementar `src/liqscope/demo/loader.py` con `DemoDataLoader`:
  1. Valida en tiempo de carga que cada fixture contenga estrictamente `_synthetic: true` y la advertencia `_notice`. Si falta este flag, lanza una excepción impidiendo su ingestión.
  2. Expone métodos tipados (`get_binance_trades`, `get_binance_force_orders`, `get_binance_open_interest`, `get_hyperliquid_positions`).
  3. **Auditoría de archivos:** Se confirma que el árbol de directorios contiene exclusivamente los 28 archivos correspondientes al plan aprobado (documentación, CI, config, fixtures, src/liqscope/ y tests/), sin archivos espurios ni dependencias no autorizadas.

---

## ADR-009: Especificación Oficial de Rate Limits y Streams de Binance Futures
- **Fecha:** 2026-10-22
- **Estado:** Aceptado
- **Contexto:** Es imperativo conocer los límites exactos de la API para configurar limitadores de tasa y colas de ingesta sin riesgo de bloqueos HTTP 429/418.
- **Fuentes Oficiales:**
  - [Binance Futures General Info - Rate Limits](https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info#rate-limits)
  - [Binance Futures WebSocket Streams - Liquidation Order Streams](https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Liquidation-Order-Streams)
- **Decisión:**
  1. **REST Rate Limits:** Fijar el presupuesto de peticiones respetando el límite por defecto de **2400 request weight/minuto por IP** (`X-MBX-USED-WEIGHT-1M`).
  2. **Stream `forceOrder`:** El ritmo de actualización oficial de Binance es de **1000 ms** y solo entrega la orden forzada de mayor tamaño del intervalo. Por consiguiente, `forceOrder` no satura la red pero representa un límite inferior muestreado.
  3. **Stream `aggTrade`:** Se procesa como flujo de alta frecuencia (push continuo en tiempo real).
