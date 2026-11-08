"""Plantilla y generador del Dashboard HTML interactivo para LiqScope.

Incorpora el sistema de diseño institutional 'Terminal Heat' (Stitch) con:
- Paleta de alta densidad cyber-financiera (Graphite/Slate Navy, Neon Cyan, Emerald, Amber, Crimson).
- Tipografía Inter (estructural) y JetBrains Mono (cuantitativa/telemetría).
- Iconografía Google Material Symbols Outlined.
- Navegación multi-pestaña: Mapa de Calor, Modelo & Datos, Niveles MMR & Simulador, Alertas.
- Conexión asíncrona en vivo con auto-refresco cada 2 minutos (120 s) y cuenta regresiva.
"""

from __future__ import annotations

DASHBOARD_HTML = """<!DOCTYPE html>
<html class="dark" lang="es">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" name="viewport"/>
  <title>LiqScope — Liquidation Heatmap • Terminal Telemetry</title>

  <!-- Google Fonts: Inter, JetBrains Mono & Material Symbols -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>

  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            "surface": "#10131a",
            "surface-dim": "#10131a",
            "surface-bright": "#363940",
            "surface-container-lowest": "#0b0e14",
            "surface-container-low": "#191c22",
            "surface-container": "#1d2026",
            "surface-container-high": "#272a31",
            "surface-container-highest": "#32353c",
            "on-surface": "#e1e2eb",
            "on-surface-variant": "#bbc9cf",
            "outline": "#859399",
            "outline-variant": "#3c494e",
            "primary": "#a5e7ff",
            "on-primary": "#003543",
            "primary-container": "#00d2ff",
            "on-primary-container": "#00566a",
            "secondary": "#ffdb9d",
            "secondary-container": "#feb700",
            "on-secondary": "#412d00",
            "secondary-fixed-dim": "#ffba20",
            "tertiary": "#3bfc89",
            "tertiary-container": "#00de72",
            "on-tertiary": "#003918",
            "tertiary-fixed": "#62ff96",
            "error": "#ff3d57",
            "error-container": "#93000a",
            "on-error": "#690005"
          },
          fontFamily: {
            sans: ["Inter", "system-ui", "sans-serif"],
            mono: ["JetBrains Mono", "monospace"]
          }
        }
      }
    };
  </script>

  <style>
    body {
      background-color: #10131a;
      color: #e1e2eb;
      font-family: 'Inter', system-ui, sans-serif;
      overflow-x: hidden;
    }
    .font-mono {
      font-family: 'JetBrains Mono', monospace;
      font-feature-settings: "tnum" 1;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 4px;
      height: 4px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: #0b0e14;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: #272a31;
      border-radius: 4px;
    }
    .laser-glow {
      box-shadow: 0 0 12px rgba(0, 210, 255, 0.45);
    }
    .amber-glow {
      box-shadow: 0 0 14px rgba(254, 183, 0, 0.35);
    }
    .emerald-glow {
      box-shadow: 0 0 14px rgba(0, 222, 114, 0.35);
    }
  </style>
</head>

<body class="bg-surface text-on-surface antialiased flex flex-col min-h-screen selection:bg-primary-container selection:text-on-primary-container pb-20">

  <!-- TOP INSTITUTIONAL TELEMETRY HEADER -->
  <header class="fixed top-0 inset-x-0 z-50 bg-surface/90 backdrop-blur-xl border-b border-surface-container-high shadow-lg">
    <div class="max-w-6xl mx-auto px-4 py-2.5 flex flex-col md:flex-row md:items-center justify-between gap-2.5">

      <!-- Brand & Status -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg bg-surface-container-high border border-primary-container/30 flex items-center justify-center text-primary-container">
            <span class="material-symbols-outlined text-[20px]">radar</span>
          </div>
          <div class="flex flex-col">
            <div class="flex items-center gap-1.5">
              <span class="font-bold text-base tracking-tight text-white leading-none">LiqScope</span>
              <span class="px-1.5 py-0.2 bg-primary-container/15 text-primary-container text-[10px] font-mono font-bold rounded uppercase">Terminal</span>
            </div>
            <span class="text-[10px] font-mono text-outline uppercase tracking-wider">Institutional Telemetry • Binance USDⓢ-M</span>
          </div>
        </div>

        <!-- Mobile Live & Timer status -->
        <div class="flex md:hidden items-center gap-2">
          <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-surface-container-high/80">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-tertiary opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-tertiary"></span>
            </span>
            <span class="text-[10px] font-mono text-tertiary font-bold uppercase tracking-widest" id="header-feed-badge-mob">LIVE</span>
          </div>
          <span class="text-[10px] font-mono text-primary font-bold" id="countdown-text-mob">02:00</span>
        </div>
      </div>

      <!-- Center: Pair & Mode Selector -->
      <div class="flex items-center gap-2 overflow-x-auto">
        <div class="inline-flex rounded-lg border border-surface-container-high p-0.5 bg-surface-container-low">
          <button id="btn-btc" onclick="selectSymbol('BTCUSDT')" class="px-3 py-1 text-xs font-mono font-bold rounded bg-primary-container text-on-primary-container shadow transition-all">BTCUSDT</button>
          <button id="btn-eth" onclick="selectSymbol('ETHUSDT')" class="px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all">ETHUSDT</button>
        </div>

        <div class="inline-flex rounded-lg border border-surface-container-high p-0.5 bg-surface-container-low">
          <button id="btn-live" onclick="setSource('live')" class="px-2.5 py-1 text-xs font-mono font-semibold rounded bg-tertiary/20 text-tertiary border border-tertiary/30 transition-all">Live Feed</button>
          <button id="btn-demo" onclick="setSource('demo')" class="px-2.5 py-1 text-xs font-mono font-semibold rounded text-on-surface-variant hover:text-white transition-all">Demo</button>
        </div>

        <!-- Manual Link Button -->
        <button onclick="switchTab('manual')" class="px-2.5 py-1 text-xs font-mono font-semibold rounded-lg border border-surface-container-high bg-surface-container-low hover:bg-surface-container text-outline hover:text-primary transition-all flex items-center gap-1 shadow-sm" title="Abrir Manual de Usuario y Guía Técnica">
          <span class="material-symbols-outlined text-[15px] text-primary">menu_book</span>
          <span>Manual</span>
        </button>
      </div>

      <!-- Right: Live Mark Telemetry & Auto Countdown -->
      <div class="hidden md:flex items-center gap-3">
        <!-- 2-min Countdown badge -->
        <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg border border-surface-container-high bg-surface-container-low" title="Auto-actualización cada 2 minutos (120 s)">
          <span class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span>
          <span class="text-[11px] font-mono text-outline">Auto:</span>
          <span id="countdown-text" class="text-[11px] font-mono font-bold text-tertiary">02:00</span>
        </div>

        <button onclick="fetchHeatmap(true)" class="p-1.5 rounded-lg border border-surface-container-high bg-surface-container-low hover:bg-surface-container text-outline hover:text-primary transition-colors" title="Actualizar ahora">
          <span class="material-symbols-outlined text-[18px]">refresh</span>
        </button>

        <!-- Live Mark Indicator -->
        <div class="flex flex-col items-end border-l border-surface-container-high pl-3">
          <span class="text-[9px] font-mono text-outline uppercase tracking-wider">PRECIO MARK</span>
          <div class="flex items-center gap-1">
            <span id="header-mark-price" class="text-base font-mono font-bold text-primary-container tracking-tight">$81,420.50</span>
            <span class="w-1.5 h-1.5 rounded-full bg-primary-container animate-ping"></span>
          </div>
        </div>
      </div>

    </div>
  </header>

  <!-- MAIN VIEWPORT CONTAINER -->
  <main class="max-w-6xl mx-auto px-3 md:px-4 pt-28 md:pt-24 w-full flex flex-col space-y-4">

    <!-- TAB 1: MAPA DE CALOR (HEATMAP TELEMETRY) -->
    <div id="tab-mapa-de-calor" class="tab-pane flex flex-col space-y-3.5">

      <!-- Regulatory Disclaimer Banner -->
      <div class="w-full bg-surface-container-low border border-surface-container-high rounded-xl p-3 flex items-start gap-2.5 shadow-sm">
        <span class="material-symbols-outlined text-secondary-container text-[20px] shrink-0 mt-0.5">shield</span>
        <div class="flex flex-col min-w-0">
          <div class="flex items-center gap-2 mb-0.5">
            <span class="font-mono text-[10px] font-bold text-secondary uppercase tracking-wider">Aviso Regulatorio Institucional</span>
            <span class="px-1.5 py-0.2 bg-surface-container-highest text-on-surface-variant font-mono text-[9px] rounded font-semibold">LECTURA PURA</span>
          </div>
          <p class="font-mono text-[10px] text-outline leading-tight">
            Herramienta analítica de solo lectura con fines educativos e informativos. LiqScope no gestiona fondos ni ejecuta órdenes. Los datos reflejan cálculos algorítmicos derivados de libros de órdenes y Open Interest real.
          </p>
        </div>
      </div>

      <!-- Telemetry Sub-Bar / OI Feed Badge -->
      <div class="w-full bg-surface-container border border-surface-container-high rounded-xl p-3 shadow-sm flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2.5">
        <div class="flex items-center gap-2">
          <span id="hero-symbol-badge" class="font-mono text-sm font-bold text-white">BTC/USDT USDⓈ-M</span>
          <span class="px-2 py-0.5 rounded bg-tertiary/15 text-tertiary font-mono text-[10px] font-bold uppercase flex items-center gap-1 border border-tertiary/20">
            <span class="material-symbols-outlined text-[13px]">verified</span>
            Binance Feed 100% Real
          </span>
          <span id="sync-time-badge" class="text-[10px] font-mono text-outline ml-auto md:ml-2">Sinc: --:--:--</span>
        </div>

        <div class="flex items-center justify-between md:justify-end gap-4 bg-surface-container-lowest/80 rounded-lg px-3 py-1.5 border border-surface-container-high/60">
          <div class="flex flex-col">
            <span class="text-[9px] font-mono text-outline uppercase tracking-wider">Open Interest Global</span>
            <span id="metric-oi-usd" class="font-mono text-xs md:text-sm text-white font-bold">$7,742.85M <span class="text-outline text-[10px]">USD</span></span>
          </div>
          <div class="flex flex-col items-end">
            <span class="text-[9px] font-mono text-outline uppercase tracking-wider">Equivalente Moneda</span>
            <span id="metric-oi-coins" class="font-mono text-xs md:text-sm text-primary font-bold">~95,120 BTC</span>
          </div>
        </div>
      </div>

      <!-- Controls Strip: Bin Selector & Quick Leverage Chips -->
      <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2 bg-surface-container-low border border-surface-container-high p-2.5 rounded-xl">

        <div class="flex flex-wrap items-center gap-2">
          <span class="text-[10px] font-mono text-outline uppercase tracking-wider flex items-center gap-1">
            <span class="material-symbols-outlined text-[14px] text-primary-container">tune</span>
            Bins:
          </span>
          <select id="select-bin-size" onchange="fetchHeatmap(true)" class="px-2.5 py-1 text-xs font-mono rounded bg-surface-container border border-surface-container-high text-white focus:outline-none focus:border-primary-container">
            <option value="10">10 USD (ETH Óptimo)</option>
            <option value="25">25 USD</option>
            <option value="50" selected>50 USD (BTC Estándar)</option>
            <option value="100">100 USD</option>
            <option value="250">250 USD</option>
            <option value="500">500 USD</option>
          </select>

          <!-- Range inputs -->
          <input type="number" id="input-min" placeholder="Min USD" onchange="fetchHeatmap(true)" class="w-24 px-2 py-1 text-xs font-mono rounded bg-surface-container border border-surface-container-high text-white placeholder-slate-500">
          <input type="number" id="input-max" placeholder="Max USD" onchange="fetchHeatmap(true)" class="w-24 px-2 py-1 text-xs font-mono rounded bg-surface-container border border-surface-container-high text-white placeholder-slate-500">
          <button onclick="resetFilters()" class="text-xs font-mono text-outline hover:text-primary underline px-1" title="Restablecer">Reset</button>
        </div>

        <!-- Quick Leverage Chips -->
        <div class="flex items-center gap-1.5 overflow-x-auto pb-0.5 no-scrollbar" id="leverageChips">
          <span class="text-[9px] font-mono text-outline uppercase tracking-wider mr-1 hidden sm:inline">Apalancamiento:</span>
          <button onclick="filterByLeverage(0)" class="lev-chip px-2.5 py-0.5 rounded bg-primary-container text-on-primary-container font-mono text-[11px] font-bold transition-all shadow-sm">Todos</button>
          <button onclick="filterByLeverage(5)" class="lev-chip px-2.5 py-0.5 rounded bg-surface-container text-outline hover:text-white font-mono text-[11px] font-semibold transition-all">5x</button>
          <button onclick="filterByLeverage(10)" class="lev-chip px-2.5 py-0.5 rounded bg-surface-container text-outline hover:text-white font-mono text-[11px] font-semibold transition-all">10x</button>
          <button onclick="filterByLeverage(25)" class="lev-chip px-2.5 py-0.5 rounded bg-surface-container text-outline hover:text-white font-mono text-[11px] font-semibold transition-all">25x</button>
          <button onclick="filterByLeverage(50)" class="lev-chip px-2.5 py-0.5 rounded bg-surface-container text-outline hover:text-white font-mono text-[11px] font-semibold transition-all">50x</button>
          <button onclick="filterByLeverage(100)" class="lev-chip px-2.5 py-0.5 rounded bg-surface-container text-outline hover:text-white font-mono text-[11px] font-semibold transition-all flex items-center gap-0.5">
            <span class="material-symbols-outlined text-[12px] text-secondary-container">bolt</span>100x
          </button>
        </div>

      </div>

      <!-- HEATMAP VISUALIZER CANVAS CARD -->
      <div class="w-full bg-surface-container-lowest border border-surface-container-high rounded-xl p-3 md:p-4 relative overflow-hidden shadow-2xl flex flex-col gap-3">

        <!-- Top HUD Over Heatmap -->
        <div class="flex items-center justify-between z-10 border-b border-surface-container-high/60 pb-2">
          <div class="flex items-center gap-2">
            <div class="flex items-center gap-1.5 bg-surface-container-high/90 px-2.5 py-1 rounded-md">
              <span class="inline-block w-2 h-2 rounded-full bg-secondary-container animate-pulse"></span>
              <span class="font-mono text-[11px] text-secondary font-bold uppercase tracking-tight">Pools Concentrados</span>
            </div>
            <span id="visible-vol-badge" class="font-mono text-[11px] text-outline hidden sm:inline">Volumen Visible: $7,742M</span>
          </div>

          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5 text-xs font-mono">
              <span class="w-2.5 h-2.5 rounded bg-error"></span>
              <span class="text-slate-300">Shorts</span>
            </div>
            <div class="flex items-center gap-1.5 text-xs font-mono">
              <span class="w-2.5 h-2.5 rounded bg-tertiary"></span>
              <span class="text-slate-300">Longs</span>
            </div>
          </div>
        </div>

        <!-- Ambient Thermal Glow Overlays -->
        <div class="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(ellipse_at_80%_20%,rgba(254,183,0,0.35)_0%,transparent_60%)]"></div>
        <div class="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(ellipse_at_80%_80%,rgba(0,222,114,0.3)_0%,transparent_55%)]"></div>

        <!-- Price Ladder Matrix Container -->
        <div id="ladder-container" class="space-y-1.5 max-h-[520px] overflow-y-auto custom-scroll pr-1.5 z-10">
          <!-- Rendered dynamically -->
        </div>

        <!-- Heat Legend and Depth Gradient Scale -->
        <div class="flex flex-col sm:flex-row items-center justify-between pt-2 border-t border-surface-container-high/60 gap-2 text-xs font-mono text-outline">
          <div class="flex items-center gap-2">
            <span>Densidad de Liquidez:</span>
            <span>Baja</span>
            <div class="w-28 h-2 rounded-full bg-gradient-to-r from-surface-container-high via-secondary-container to-tertiary"></div>
            <span class="text-tertiary font-bold">Ultra Alta ($500M+)</span>
          </div>
          <div class="flex items-center gap-2">
            <span id="coverage-badge" class="text-tertiary font-bold">Cobertura: 100.0%</span>
          </div>
        </div>

      </div>

      <!-- SUMMARY RISK METRICS (3 BENTO TILES) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5">

        <!-- Short Liquidation Risk Tile -->
        <div class="w-full bg-surface-container border border-surface-container-high rounded-xl p-3 shadow-sm flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-lg bg-secondary-container/15 flex items-center justify-center shrink-0 border border-secondary-container/30">
              <span class="material-symbols-outlined text-secondary-container text-[20px]">arrow_circle_up</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-on-surface-variant font-medium">Shorts en Riesgo</span>
              <span class="font-mono text-[10px] text-secondary font-semibold">Barrida a la resistencia</span>
            </div>
          </div>
          <div class="flex flex-col items-end">
            <span id="tile-short-vol" class="font-mono text-sm md:text-base text-secondary-container font-extrabold tracking-tight">$3,871.4M</span>
            <span class="font-mono text-[9px] text-outline">Volumen Expuesto</span>
          </div>
        </div>

        <!-- Long Liquidation Risk Tile -->
        <div class="w-full bg-surface-container border border-surface-container-high rounded-xl p-3 shadow-sm flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-lg bg-tertiary/15 flex items-center justify-center shrink-0 border border-tertiary/30">
              <span class="material-symbols-outlined text-tertiary text-[20px]">arrow_circle_down</span>
            </div>
            <div class="flex flex-col">
              <span class="text-xs text-on-surface-variant font-medium">Longs en Riesgo</span>
              <span class="font-mono text-[10px] text-tertiary font-semibold">Soporte dinámico</span>
            </div>
          </div>
          <div class="flex flex-col items-end">
            <span id="tile-long-vol" class="font-mono text-sm md:text-base text-tertiary font-extrabold tracking-tight">$3,871.4M</span>
            <span class="font-mono text-[9px] text-outline">Volumen Expuesto</span>
          </div>
        </div>

        <!-- Long / Short Ratio Bar Tile -->
        <div class="w-full bg-surface-container border border-surface-container-high rounded-xl p-3 shadow-sm flex flex-col justify-between gap-1.5">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-1.5">
              <span class="text-xs text-on-surface-variant font-medium">Ratio Long / Short OI</span>
              <span id="ratio-mode-pill" class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-tertiary/15 text-tertiary border border-tertiary/20 font-bold uppercase">LIVE</span>
            </div>
            <div class="flex items-center gap-2 font-mono text-xs">
              <span id="ratio-long-text" class="text-tertiary font-bold">50.0% Long</span>
              <span class="text-outline">/</span>
              <span id="ratio-short-text" class="text-secondary font-bold">50.0% Short</span>
            </div>
          </div>
          <!-- Dual Segment Progress Bar -->
          <div class="w-full h-2 rounded-full bg-surface-container-lowest overflow-hidden flex border border-surface-container-high">
            <div id="ratio-long-bar" class="h-full bg-tertiary transition-all duration-500" style="width: 50%"></div>
            <div id="ratio-short-bar" class="h-full bg-secondary-container transition-all duration-500" style="width: 50%"></div>
          </div>
        </div>

      </div>

      <!-- ZONA DE MAYOR MAGNETISMO (CALLOUT CARD) -->
      <div class="w-full bg-surface-container-high border border-surface-container-highest rounded-xl p-3.5 shadow-md flex flex-col gap-2 relative overflow-hidden">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="material-symbols-outlined text-secondary-container text-[20px]">attractions</span>
            <span class="text-sm font-bold text-white tracking-tight">Zona de Mayor Magnetismo</span>
          </div>
          <span class="px-2 py-0.5 rounded bg-secondary-container/20 text-secondary-container font-mono text-[10px] font-bold uppercase border border-secondary-container/30">
            Foco de Atracción
          </span>
        </div>

        <div class="flex items-baseline justify-between pt-1">
          <div class="flex flex-col">
            <span id="magnet-price" class="font-mono text-lg md:text-xl text-secondary-container font-extrabold">$83,000</span>
            <span id="magnet-dist" class="font-mono text-[10px] text-outline">Distancia al Mark: +1.84% (~$1,500.00)</span>
          </div>
          <div class="flex flex-col items-end">
            <span id="magnet-vol" class="font-mono text-sm md:text-base text-white font-bold">$1,140.2M</span>
            <span id="magnet-lev" class="font-mono text-[10px] text-tertiary uppercase">Apalancamiento 25x-50x</span>
          </div>
        </div>

        <p class="text-xs text-on-surface-variant leading-relaxed">
          Concentración crítica de órdenes de parada y límites forzados. Alta probabilidad de mecha liquidadora rápida si el precio supera el rango de consolidación actual.
        </p>

        <!-- Interactive CTA to Inspect Cluster -->
        <button class="mt-1 w-full py-2 bg-primary-container text-on-primary-container hover:brightness-110 active:scale-[0.99] transition-all rounded-lg font-bold text-xs flex items-center justify-center gap-2 shadow-md" id="inspectClusterBtn" onclick="inspectCluster()">
          <span class="material-symbols-outlined text-[18px]">radar</span>
          <span>Inspeccionar Desglose Institucional del Clúster</span>
        </button>

        <!-- Inspection Drawer -->
        <div class="hidden w-full bg-surface-container rounded-lg p-3 flex-col gap-2 border border-surface-container-high mt-2" id="clusterInspectionPanel">
          <div class="flex items-center justify-between pb-1 border-b border-surface-container-high">
            <div class="flex items-center gap-1.5">
              <span class="material-symbols-outlined text-primary text-[18px]">travel_explore</span>
              <span id="inspect-cluster-title" class="text-xs font-bold text-white">Desglose del Clúster</span>
            </div>
            <button onclick="closeInspection()" class="text-outline hover:text-white text-xs font-mono">Cerrar [×]</button>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-2 pt-1 font-mono text-xs">
            <div class="bg-surface-container-low p-2 rounded">
              <span class="text-outline text-[10px] block">Tier / Apalancamiento</span>
              <span id="inspect-tier" class="font-bold text-white">25x (MMR 1.0%)</span>
            </div>
            <div class="bg-surface-container-low p-2 rounded">
              <span class="text-outline text-[10px] block">Delta Requerido</span>
              <span id="inspect-delta" class="font-bold text-secondary">3.00%</span>
            </div>
            <div class="bg-surface-container-low p-2 rounded">
              <span class="text-outline text-[10px] block">Volumen Estimado</span>
              <span id="inspect-vol" class="font-bold text-primary">$1,140.2M</span>
            </div>
            <div class="bg-surface-container-low p-2 rounded">
              <span class="text-outline text-[10px] block">Riesgo de Cascada</span>
              <span id="inspect-risk" class="font-bold text-error">ELEVADO</span>
            </div>
          </div>
        </div>

      </div>

    </div>

    <!-- TAB 2: MODELO & DATOS (CRYPTOGRAPHIC TRANSPARENCY) -->
    <div id="tab-modelo-datos" class="tab-pane hidden flex flex-col space-y-3.5">

      <!-- Integrity Protocol Banner -->
      <div class="rounded-xl bg-surface-container-high border border-surface-container-highest p-4 shadow-md">
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary-container text-[24px]">verified_user</span>
            <div>
              <span class="font-mono text-[10px] uppercase tracking-widest text-primary-container font-bold">Protocolo de Integridad</span>
              <h2 class="text-base font-bold text-white">Transparencia Criptográfica de Datos</h2>
            </div>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-surface-container-lowest text-tertiary font-mono text-[10px] flex items-center gap-1 border border-tertiary/20">
            <span class="w-1.5 h-1.5 rounded-full bg-tertiary animate-ping"></span>
            Binance Live Sync
          </span>
        </div>
        <p class="text-xs text-on-surface-variant mt-2 leading-relaxed">
          ¿La información proyectada es real o estimada? A continuación desglosamos la frontera exacta entre la telemetría fiduciaria cruda y el modelado probabilístico institucional.
        </p>
      </div>

      <!-- SECTION: 100% LIVE TELEMETRY (OBSERVED) -->
      <div class="flex flex-col space-y-2.5">
        <div class="flex items-center justify-between px-1">
          <div class="flex items-center gap-2">
            <div class="w-5 h-5 rounded-full bg-tertiary/20 flex items-center justify-center">
              <span class="material-symbols-outlined text-tertiary text-[14px]">shield</span>
            </div>
            <h3 class="text-xs font-bold text-white uppercase tracking-wider">Datos 100% REALES en Vivo</h3>
          </div>
          <span class="font-mono text-[10px] text-tertiary bg-tertiary/10 px-2 py-0.5 rounded-full border border-tertiary/20">Binance L1 Direct Sync</span>
        </div>

        <!-- Telemetry Items -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">

          <!-- Item A: Mark Price -->
          <div class="bg-surface-container border border-surface-container-high rounded-xl p-3 space-y-2">
            <div class="flex items-start justify-between">
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full bg-tertiary animate-pulse"></span>
                  <span class="font-mono text-xs font-bold text-white">Precio Mark (mark_price)</span>
                </div>
                <span class="text-[11px] text-on-surface-variant">Binance Futures USDⓈ-M Perps</span>
              </div>
              <span id="model-mark-display" class="font-mono text-base font-bold text-tertiary">$81,420.50</span>
            </div>
            <div class="bg-surface-container-lowest p-2 rounded flex items-center justify-between gap-2 border border-surface-container-high/60">
              <span class="font-mono text-[10px] text-outline truncate">GET fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT</span>
              <a href="https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT" target="_blank" class="text-primary-container hover:underline text-[10px] font-mono shrink-0">Verificar ↗</a>
            </div>
          </div>

          <!-- Item B: Open Interest -->
          <div class="bg-surface-container border border-surface-container-high rounded-xl p-3 space-y-2">
            <div class="flex items-start justify-between">
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="material-symbols-outlined text-secondary text-[16px]">pie_chart</span>
                  <span class="font-mono text-xs font-bold text-white">Interés Abierto Total</span>
                </div>
                <span class="text-[11px] text-on-surface-variant">total_open_interest_usd</span>
              </div>
              <span id="model-oi-display" class="font-mono text-base font-bold text-secondary">~$7,742M</span>
            </div>
            <div class="bg-surface-container-lowest p-2 rounded flex items-center justify-between gap-2 border border-surface-container-high/60">
              <span class="font-mono text-[10px] text-outline truncate">GET fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT</span>
              <a href="https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT" target="_blank" class="text-primary-container hover:underline text-[10px] font-mono shrink-0">Verificar ↗</a>
            </div>
          </div>

        </div>

      </div>

      <!-- SECTION: MODELADO ANALÍTICO Y FÓRMULAS -->
      <div class="bg-surface-container border border-surface-container-high rounded-xl p-4 space-y-3">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary text-[20px]">functions</span>
          <h3 class="text-xs font-bold text-white uppercase tracking-wider">Fórmulas Oficiales de Liquidación con MMR</h3>
        </div>

        <p class="text-xs text-on-surface-variant leading-relaxed">
          Ningún exchange revela precios de entrada privados. LiqScope aplica las fórmulas matemáticas oficiales de Binance para proyectar los niveles de liquidación forzosa:
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <div class="bg-surface-container-lowest p-3 rounded-lg border border-tertiary/20 space-y-1">
            <span class="text-tertiary font-bold block">Fórmula de Liquidación LONG:</span>
            <code class="text-white block bg-surface-container p-2 rounded">LiqPrice = EntryPrice × (1 - 1/Lev + MMR)</code>
            <span class="text-outline text-[10px] block">Ej: 50x (MMR 0.5%) → Caída del 1.50% hasta liquidación</span>
          </div>

          <div class="bg-surface-container-lowest p-3 rounded-lg border border-error/20 space-y-1">
            <span class="text-error font-bold block">Fórmula de Liquidación SHORT:</span>
            <code class="text-white block bg-surface-container p-2 rounded">LiqPrice = EntryPrice × (1 + 1/Lev - MMR)</code>
            <span class="text-outline text-[10px] block">Ej: 50x (MMR 0.5%) → Subida del 1.50% hasta liquidación</span>
          </div>
        </div>
      </div>

    </div>

    <!-- TAB 3: NIVELES MMR & SIMULADOR -->
    <div id="tab-niveles-mmr" class="tab-pane hidden flex flex-col space-y-3.5">

      <!-- Sub-header HUD -->
      <div class="flex items-center justify-between px-3 py-2 rounded-xl bg-surface-container-low border border-surface-container-high">
        <div class="flex items-center gap-2">
          <div class="w-7 h-7 rounded-lg bg-surface-container flex items-center justify-center text-primary-container">
            <span class="material-symbols-outlined text-[18px]">functions</span>
          </div>
          <div>
            <span class="text-xs font-bold text-white block">Simulador de Liquidación MMR</span>
            <span class="text-[10px] font-mono text-outline">Binance USDⓢ-M Isolated / Cross Protocol</span>
          </div>
        </div>
        <div class="flex flex-col items-end">
          <span class="text-[9px] font-mono text-outline uppercase">Mark Referencia</span>
          <span id="sim-ref-mark" class="text-xs font-mono font-bold text-tertiary">$81,420.50</span>
        </div>
      </div>

      <!-- Simulator Card -->
      <div class="rounded-xl bg-surface-container border border-surface-container-high p-4 space-y-4 shadow-md">

        <!-- Direction Selector Toggle -->
        <div class="grid grid-cols-2 gap-2 p-1 rounded-lg bg-surface-container-lowest border border-surface-container-high">
          <button id="sim-btn-long" onclick="setSimDirection('LONG')" class="py-2 px-3 rounded font-mono text-xs font-bold transition-all bg-tertiary-container text-on-tertiary flex items-center justify-center gap-1.5">
            <span class="material-symbols-outlined text-[16px]">trending_up</span>
            <span>POSICIÓN LONG</span>
          </button>
          <button id="sim-btn-short" onclick="setSimDirection('SHORT')" class="py-2 px-3 rounded font-mono text-xs font-bold transition-all text-on-surface-variant hover:text-white flex items-center justify-center gap-1.5">
            <span class="material-symbols-outlined text-[16px]">trending_down</span>
            <span>POSICIÓN SHORT</span>
          </button>
        </div>

        <!-- Entry Price & Usar Mark -->
        <div class="space-y-1">
          <div class="flex justify-between items-center text-xs">
            <label class="text-on-surface-variant font-mono">Precio de Entrada (USDT)</label>
            <button onclick="useMarkInSim()" class="text-primary-container font-mono text-xs hover:underline flex items-center gap-1">
              <span class="material-symbols-outlined text-[13px]">bolt</span>Usar Mark Actual
            </button>
          </div>
          <div class="flex items-center rounded-lg bg-surface-container-lowest px-3 py-2 border border-surface-container-high">
            <span class="font-mono text-outline mr-2">$</span>
            <input id="sim-entry-input" type="number" value="81420" oninput="recalcSimulator()" class="w-full bg-transparent font-mono text-lg font-bold text-white focus:outline-none">
            <span class="font-mono text-xs text-outline ml-2">USDT</span>
          </div>
        </div>

        <!-- Leverage Chips -->
        <div class="space-y-1.5">
          <div class="flex justify-between items-center text-xs font-mono">
            <span class="text-on-surface-variant">Apalancamiento Efectivo</span>
            <span id="sim-lev-label" class="text-secondary font-bold">50x Multiplier (MMR 0.5%)</span>
          </div>
          <div class="grid grid-cols-5 gap-2" id="sim-leverage-buttons">
            <button onclick="setSimLeverage(5, 0.04)" class="sim-lev py-2 rounded bg-surface-container-low hover:bg-surface-container-high text-outline hover:text-white font-mono text-xs font-bold transition-colors">5x</button>
            <button onclick="setSimLeverage(10, 0.02)" class="sim-lev py-2 rounded bg-surface-container-low hover:bg-surface-container-high text-outline hover:text-white font-mono text-xs font-bold transition-colors">10x</button>
            <button onclick="setSimLeverage(25, 0.01)" class="sim-lev py-2 rounded bg-surface-container-low hover:bg-surface-container-high text-outline hover:text-white font-mono text-xs font-bold transition-colors">25x</button>
            <button onclick="setSimLeverage(50, 0.005)" class="sim-lev py-2 rounded bg-primary-container text-on-primary-container font-mono text-xs font-bold shadow transition-colors">50x</button>
            <button onclick="setSimLeverage(100, 0.004)" class="sim-lev py-2 rounded bg-surface-container-low hover:bg-surface-container-high text-outline hover:text-white font-mono text-xs font-bold transition-colors">100x</button>
          </div>
        </div>

        <!-- Calculated Results HUD Panel -->
        <div class="rounded-xl bg-surface-container-lowest p-4 space-y-3 border border-surface-container-high relative overflow-hidden">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-[10px] font-mono text-outline uppercase tracking-wider block">Precio de Liquidación Estimado</span>
              <span id="sim-liq-result" class="font-mono text-2xl font-extrabold text-tertiary tracking-tight">$80,198.70</span>
            </div>
            <div class="flex flex-col items-end">
              <span class="text-[10px] font-mono text-outline uppercase tracking-wider">Distancia al Mark</span>
              <span id="sim-dist-result" class="font-mono text-sm font-bold text-secondary">-1.50%</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-2 pt-2 border-t border-surface-container-high/60 font-mono text-xs">
            <div class="bg-surface-container p-2 rounded">
              <span class="text-outline text-[10px] block">Margen Mantenimiento (MMR)</span>
              <span id="sim-mmr-badge" class="font-bold text-primary">0.50%</span>
            </div>
            <div class="bg-surface-container p-2 rounded">
              <span class="text-outline text-[10px] block">Buffer de Supervivencia</span>
              <span id="sim-buffer-badge" class="font-bold text-white">~$1,221.80 USDT</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Official Binance Tiers Table -->
      <div class="rounded-xl bg-surface-container border border-surface-container-high p-4 space-y-2">
        <span class="text-xs font-bold text-white block uppercase tracking-wider">Tabla Oficial de Escalones Binance (BTCUSDT)</span>
        <div class="overflow-x-auto">
          <table class="w-full font-mono text-xs text-left">
            <thead>
              <tr class="border-b border-surface-container-high text-outline text-[10px]">
                <th class="py-1">Nivel</th>
                <th class="py-1">Valor Nocional (USDT)</th>
                <th class="py-1">Apalancamiento</th>
                <th class="py-1">MMR</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-container-high/60 text-slate-300">
              <tr><td class="py-1 text-primary">Tier 1</td><td>0 – 50,000</td><td>100x – 125x</td><td>0.40%</td></tr>
              <tr><td class="py-1 text-primary">Tier 2</td><td>50,000 – 250,000</td><td>50x</td><td>0.50%</td></tr>
              <tr><td class="py-1 text-primary">Tier 3</td><td>250,000 – 1,000,000</td><td>25x</td><td>1.00%</td></tr>
              <tr><td class="py-1 text-primary">Tier 4</td><td>1,000,000 – 5,000,000</td><td>10x</td><td>2.00%</td></tr>
              <tr><td class="py-1 text-primary">Tier 5</td><td>5,000,000+</td><td>5x</td><td>4.00%</td></tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- TAB 4: ALERTAS & RADAR DE CLÚSTERES -->
    <div id="tab-alertas" class="tab-pane hidden flex flex-col space-y-3.5">

      <!-- Live Radar Pulse Status -->
      <div class="flex items-center justify-between px-2">
        <div class="flex items-center gap-2">
          <span class="relative flex h-2.5 w-2.5">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-error"></span>
          </span>
          <span class="font-mono text-xs font-bold text-white uppercase tracking-wider">Monitor Radar de Telemetría</span>
        </div>
        <span class="px-2 py-0.5 rounded bg-surface-container-high text-tertiary font-mono text-[10px] font-bold">RADAR ACTIVO</span>
      </div>

      <!-- Bento Stats Panel -->
      <div class="grid grid-cols-3 gap-2">
        <div class="p-3 bg-surface-container border border-surface-container-high rounded-xl">
          <span class="text-[9px] font-mono text-outline uppercase block">Alertas Activas</span>
          <div class="flex items-baseline gap-1 mt-0.5">
            <span class="font-mono text-lg font-bold text-primary">06</span>
            <span class="font-mono text-[10px] text-tertiary">LIVE</span>
          </div>
          <span class="text-[9px] font-mono text-outline">En radio &lt;2%</span>
        </div>

        <div class="p-3 bg-surface-container border border-surface-container-high rounded-xl">
          <span class="text-[9px] font-mono text-outline uppercase block">Clúster Mayor</span>
          <div class="flex items-baseline gap-1 mt-0.5">
            <span class="font-mono text-lg font-bold text-secondary">1.84%</span>
          </div>
          <span class="text-[9px] font-mono text-secondary-fixed-dim">$1,140M POOL</span>
        </div>

        <div class="p-3 bg-surface-container border border-surface-container-high rounded-xl">
          <span class="text-[9px] font-mono text-outline uppercase block">Presión Barrida</span>
          <div class="flex items-center gap-1 mt-0.5">
            <span class="font-mono text-sm font-bold text-error">ALTA</span>
            <span class="w-1.5 h-1.5 rounded-full bg-error animate-pulse"></span>
          </div>
          <span class="text-[9px] font-mono text-error">Shorts en riesgo</span>
        </div>
      </div>

      <!-- Alerts Stream Cards -->
      <div class="flex flex-col gap-2.5" id="alerts-stream">

        <!-- Alert 1 -->
        <div class="bg-surface-container border border-surface-container-high rounded-xl p-3 relative overflow-hidden flex flex-col gap-1.5">
          <div class="absolute left-0 top-0 bottom-0 w-1 bg-secondary-container"></div>
          <div class="flex items-center justify-between pl-2">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-secondary-container text-[18px]">local_fire_department</span>
              <span class="font-mono text-xs font-bold text-white">Pared de Liquidación Short Inminente</span>
            </div>
            <span class="px-1.5 py-0.2 rounded bg-secondary-container/20 text-secondary-container font-mono text-[9px] font-bold">+1.84%</span>
          </div>
          <p class="text-xs text-on-surface-variant pl-2 leading-relaxed">
            Se detecta un muro de <strong class="text-white">$1,140.2M USD</strong> en liquidaciones de posiciones cortas a 25x-50x en el rango $83,000 - $83,050.
          </p>
        </div>

        <!-- Alert 2 -->
        <div class="bg-surface-container border border-surface-container-high rounded-xl p-3 relative overflow-hidden flex flex-col gap-1.5">
          <div class="absolute left-0 top-0 bottom-0 w-1 bg-tertiary"></div>
          <div class="flex items-center justify-between pl-2">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-tertiary text-[18px]">tsunami</span>
              <span class="font-mono text-xs font-bold text-white">Soporte Dinámico de Liquidación Long</span>
            </div>
            <span class="px-1.5 py-0.2 rounded bg-tertiary/20 text-tertiary font-mono text-[9px] font-bold">-1.50%</span>
          </div>
          <p class="text-xs text-on-surface-variant pl-2 leading-relaxed">
            Cascada de <strong class="text-white">$760.1M USD</strong> en posiciones largas a 50x en el nivel de $80,250. Foco de rebote algorítmico potencial.
          </p>
        </div>

      </div>

    </div>

    <!-- TAB 5: MANUAL & GUÍA DE USO -->
    <div id="tab-manual" class="tab-pane hidden flex flex-col space-y-4">

      <!-- Header Hero Card -->
      <div class="rounded-xl bg-surface-container-high border border-surface-container-highest p-4 shadow-lg flex items-start justify-between gap-3">
        <div class="flex items-start gap-3">
          <div class="w-10 h-10 rounded-xl bg-primary-container/20 border border-primary-container/30 flex items-center justify-center text-primary-container shrink-0 mt-0.5">
            <span class="material-symbols-outlined text-[24px]">menu_book</span>
          </div>
          <div class="flex flex-col">
            <div class="flex items-center gap-2">
              <h2 class="text-base font-bold text-white">Manual de Usuario & Telemetría</h2>
              <span class="px-2 py-0.2 bg-primary-container/15 text-primary-container text-[10px] font-mono font-bold rounded uppercase">Guía Oficial</span>
            </div>
            <p class="text-xs text-on-surface-variant mt-1 leading-relaxed">
              Aprende a interpretar la matriz de calor, los clústeres de liquidación institucional estilo CoinGlass, los multiplicadores dominantes y la telemetría en vivo de Binance USDⓢ-M.
            </p>
          </div>
        </div>
        <a href="https://github.com/liqscope" target="_blank" class="hidden sm:inline-flex px-3 py-1 text-xs font-mono font-bold rounded-lg bg-surface-container-lowest border border-surface-container-high text-primary hover:underline items-center gap-1">
          GitHub Docs ↗
        </a>
      </div>

      <!-- Section 1: Concept & Data Integrity -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="bg-surface-container border border-surface-container-high rounded-xl p-3.5 space-y-2">
          <div class="flex items-center gap-2 text-white font-bold text-xs uppercase font-mono">
            <span class="material-symbols-outlined text-tertiary text-[18px]">verified</span>
            1. Datos 100% Reales en Vivo
          </div>
          <ul class="text-xs text-on-surface-variant space-y-1.5 list-disc list-inside">
            <li><strong class="text-white">Precio Mark:</strong> Servidores de producción de Binance Futures en tiempo real (<code class="text-primary font-mono text-[10px]">/fapi/v1/premiumIndex</code>).</li>
            <li><strong class="text-white">Open Interest Global:</strong> Contratos vigentes en el mercado (<code class="text-primary font-mono text-[10px]">/fapi/v1/openInterest</code>).</li>
            <li><strong class="text-white">Ratio Real de Cuentas:</strong> Porcentaje de cuentas reales en largo vs corto (<code class="text-primary font-mono text-[10px]">/futures/data/globalLongShortAccountRatio</code>).</li>
          </ul>
        </div>

        <div class="bg-surface-container border border-surface-container-high rounded-xl p-3.5 space-y-2">
          <div class="flex items-center gap-2 text-white font-bold text-xs uppercase font-mono">
            <span class="material-symbols-outlined text-secondary-container text-[18px]">functions</span>
            2. Modelado Matemático de Zonas
          </div>
          <p class="text-xs text-on-surface-variant leading-relaxed">
            Ningún exchange publica precios de entrada privados. Al igual que plataformas como CoinGlass, LiqScope proyecta el Open Interest en escalones discretos usando las fórmulas oficiales de margen de mantenimiento (<strong class="text-white">MMR</strong>) de Binance.
          </p>
        </div>
      </div>

      <!-- Section 2: Ladder Matrix Interpretation -->
      <div class="bg-surface-container border border-surface-container-high rounded-xl p-4 space-y-3">
        <div class="flex items-center gap-2 text-white font-bold text-xs uppercase font-mono">
          <span class="material-symbols-outlined text-primary text-[20px]">view_column</span>
          3. Cómo Leer la Escalera de Liquidaciones
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 font-mono text-xs">
          <div class="bg-surface-container-lowest p-3 rounded-lg border border-secondary-container/30">
            <span class="text-secondary-container font-bold block mb-1">🔥 Badge MAX LIQ</span>
            <p class="text-[11px] text-slate-300 font-sans leading-relaxed">
              Identifica el clúster con mayor acumulación de liquidez de todo el libro visible. Es el objetivo magnético prioritario del mercado.
            </p>
          </div>

          <div class="bg-surface-container-lowest p-3 rounded-lg border border-primary-container/30">
            <span class="text-primary-container font-bold block mb-1">Multiplicador [25x, 50x]</span>
            <p class="text-[11px] text-slate-300 font-sans leading-relaxed">
              Indica qué nivel de apalancamiento es el responsable principal del volumen concentrado en ese escalón de precio.
            </p>
          </div>

          <div class="bg-surface-container-lowest p-3 rounded-lg border border-tertiary/30">
            <span class="text-tertiary font-bold block mb-1">Láser Neón Mark Price</span>
            <p class="text-[11px] text-slate-300 font-sans leading-relaxed">
              Línea divisoria en vivo: los <strong class="text-secondary-container">Short Pools</strong> se sitúan siempre por encima y los <strong class="text-tertiary">Long Pools</strong> por debajo.
            </p>
          </div>
        </div>
      </div>

      <!-- Section 3: Optimal Bins Guide -->
      <div class="bg-surface-container border border-surface-container-high rounded-xl p-4 space-y-2">
        <div class="flex items-center gap-2 text-white font-bold text-xs uppercase font-mono">
          <span class="material-symbols-outlined text-primary text-[20px]">tune</span>
          4. Granularidad Óptima de Bins (BTC vs ETH)
        </div>
        <p class="text-xs text-on-surface-variant leading-relaxed">
          Para <strong class="text-white">BTCUSDT</strong> (~$75,000 USD), el tamaño recomendado es <strong class="text-primary font-mono">50 USD</strong> o <strong class="text-primary font-mono">100 USD</strong>.
          Para <strong class="text-white">ETHUSDT</strong> (~$2,200 USD), el selector se ajusta automáticamente a <strong class="text-primary font-mono">10 USD</strong> para evitar fusionar los niveles de 50x y 100x en un solo escalón.
        </p>
      </div>

    </div>

  </main>

  <!-- FIXED BOTTOM NAVIGATION BAR -->
  <nav class="fixed bottom-0 inset-x-0 z-50 bg-surface/95 backdrop-blur-xl border-t border-surface-container-high shadow-2xl">
    <div class="max-w-md mx-auto flex justify-around items-center h-16 px-2">

      <button onclick="switchTab('mapa-de-calor')" id="nav-mapa-de-calor" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-primary-container bg-surface-container-high/60 transition-all font-semibold">
        <span class="material-symbols-outlined text-[20px]">local_fire_department</span>
        <span class="font-mono text-[10px] tracking-tight">Mapa Calor</span>
      </button>

      <button onclick="switchTab('modelo-datos')" id="nav-modelo-datos" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-outline hover:text-white transition-all">
        <span class="material-symbols-outlined text-[20px]">dataset</span>
        <span class="font-mono text-[10px] tracking-tight">Modelo & Datos</span>
      </button>

      <button onclick="switchTab('niveles-mmr')" id="nav-niveles-mmr" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-outline hover:text-white transition-all">
        <span class="material-symbols-outlined text-[20px]">layers</span>
        <span class="font-mono text-[10px] tracking-tight">Niveles MMR</span>
      </button>

      <button onclick="switchTab('alertas')" id="nav-alertas" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-outline hover:text-white transition-all">
        <span class="material-symbols-outlined text-[20px]">notifications</span>
        <span class="font-mono text-[10px] tracking-tight">Alertas</span>
      </button>

      <button onclick="switchTab('manual')" id="nav-manual" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-outline hover:text-white transition-all">
        <span class="material-symbols-outlined text-[20px]">menu_book</span>
        <span class="font-mono text-[10px] tracking-tight">Manual</span>
      </button>

    </div>
  </nav>

  <!-- JAVASCRIPT CONTROLLER -->
  <script>
    let currentSymbol = 'BTCUSDT';
    let currentSource = 'live';
    let currentData = null;
    let selectedLevFilter = 0; // 0 = all

    // Simulator State
    let simDirection = 'LONG';
    let simLeverage = 50;
    let simMMR = 0.005;

    // 2-minute auto refresh countdown (120 s)
    const AUTO_REFRESH_INTERVAL_SEC = 120;
    let secondsLeft = AUTO_REFRESH_INTERVAL_SEC;
    let timerId = null;

    function resetCountdown() {
      secondsLeft = AUTO_REFRESH_INTERVAL_SEC;
      updateCountdownDisplay();
    }

    function updateCountdownDisplay() {
      const min = Math.floor(secondsLeft / 60);
      const sec = secondsLeft % 60;
      const formatted = `${min < 10 ? '0' : ''}${min}:${sec < 10 ? '0' : ''}${sec}`;
      const el = document.getElementById('countdown-text');
      const elMob = document.getElementById('countdown-text-mob');
      if (el) el.innerText = formatted;
      if (elMob) elMob.innerText = formatted;
    }

    function startAutoRefreshTimer() {
      if (timerId) clearInterval(timerId);
      updateCountdownDisplay();
      timerId = setInterval(() => {
        secondsLeft--;
        if (secondsLeft <= 0) {
          fetchHeatmap(true);
        } else {
          updateCountdownDisplay();
        }
      }, 1000);
    }

    // Tab Navigation
    function switchTab(tabId) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
      const activeTab = document.getElementById('tab-' + tabId);
      if (activeTab) activeTab.classList.remove('hidden');

      document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.className = 'nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-outline hover:text-white transition-all';
      });
      const activeNav = document.getElementById('nav-' + tabId);
      if (activeNav) {
        activeNav.className = 'nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1.5 rounded-lg text-primary-container bg-surface-container-high/60 transition-all font-semibold';
      }
    }

    // Symbol & Source Selectors
    function selectSymbol(sym) {
      currentSymbol = sym;
      document.getElementById('btn-btc').className = sym === 'BTCUSDT' ? 'px-3 py-1 text-xs font-mono font-bold rounded bg-primary-container text-on-primary-container shadow transition-all' : 'px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all';
      document.getElementById('btn-eth').className = sym === 'ETHUSDT' ? 'px-3 py-1 text-xs font-mono font-bold rounded bg-primary-container text-on-primary-container shadow transition-all' : 'px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all';
      document.getElementById('hero-symbol-badge').innerText = sym === 'BTCUSDT' ? 'BTC/USDT USDⓈ-M' : 'ETH/USDT USDⓈ-M';

      // Auto-adapt bin size: 10 for ETH, 50 for BTC
      const binSelect = document.getElementById('select-bin-size');
      if (binSelect) {
        if (sym === 'ETHUSDT' && (binSelect.value === '50' || binSelect.value === '100')) {
          binSelect.value = '10';
        } else if (sym === 'BTCUSDT' && binSelect.value === '10') {
          binSelect.value = '50';
        }
      }
      fetchHeatmap(true);
    }

    function setSource(src) {
      currentSource = src;
      document.getElementById('btn-live').className = src === 'live' ? 'px-2.5 py-1 text-xs font-mono font-semibold rounded bg-tertiary/20 text-tertiary border border-tertiary/30 transition-all' : 'px-2.5 py-1 text-xs font-mono font-semibold rounded text-on-surface-variant hover:text-white transition-all';
      document.getElementById('btn-demo').className = src === 'demo' ? 'px-2.5 py-1 text-xs font-mono font-semibold rounded bg-primary-container/20 text-primary-container border border-primary-container/30 transition-all' : 'px-2.5 py-1 text-xs font-mono font-semibold rounded text-on-surface-variant hover:text-white transition-all';
      fetchHeatmap(true);
    }

    function resetFilters() {
      document.getElementById('input-min').value = '';
      document.getElementById('input-max').value = '';
      document.getElementById('select-bin-size').value = '50';
      selectedLevFilter = 0;
      updateLevChipsUI();
      fetchHeatmap(true);
    }

    function filterByLeverage(lev) {
      selectedLevFilter = lev;
      updateLevChipsUI();
      if (currentData) renderHeatmap(currentData);
    }

    function updateLevChipsUI() {
      const chips = document.querySelectorAll('#leverageChips .lev-chip');
      chips.forEach((btn, idx) => {
        const levValues = [0, 5, 10, 25, 50, 100];
        if (levValues[idx] === selectedLevFilter) {
          btn.className = 'lev-chip px-2.5 py-0.5 rounded bg-primary-container text-on-primary-container font-mono text-[11px] font-bold transition-all shadow-sm';
        } else {
          btn.className = 'lev-chip px-2.5 py-0.5 rounded bg-surface-container text-outline hover:text-white font-mono text-[11px] font-semibold transition-all';
        }
      });
    }

    // Heatmap API Fetch
    async function fetchHeatmap(resetTimer = false) {
      if (resetTimer) resetCountdown();

      const minP = document.getElementById('input-min').value;
      const maxP = document.getElementById('input-max').value;
      const binSize = document.getElementById('select-bin-size').value || '50';

      let url = `/api/v1/heatmap/${currentSymbol}?bin_size=${binSize}&source=${currentSource}`;
      if (minP) url += `&min_price=${minP}`;
      if (maxP) url += `&max_price=${maxP}`;

      try {
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          currentData = data;
          renderHeatmap(data);
          updateModelView(data);
          updateSimulatorFromData(data);
          return;
        }
      } catch (err) {
        console.warn('Live API fetch warning:', err);
      }
    }

    // Render Heatmap Matrix
    function renderHeatmap(data) {
      const formattedPrice = `$${data.current_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      document.getElementById('header-mark-price').innerText = formattedPrice;
      document.getElementById('metric-oi-usd').innerHTML = `$${(data.total_open_interest_usd / 1e6).toFixed(2)}M <span class="text-outline text-[10px]">USD</span>`;

      const coinsEst = (data.total_open_interest_usd / data.current_price).toFixed(0);
      document.getElementById('metric-oi-coins').innerText = `~${Number(coinsEst).toLocaleString()} ${currentSymbol.replace('USDT','')}`;
      document.getElementById('visible-vol-badge').innerText = `Volumen Visible: $${(data.visible_bin_volume_usd / 1e6).toFixed(1)}M`;
      document.getElementById('coverage-badge').innerText = `Cobertura: ${data.coverage_pct.toFixed(1)}%`;
      document.getElementById('sync-time-badge').innerText = `Sinc: ${new Date().toLocaleTimeString()}`;

      // H-03: Sincronizar badge de origen dinámicamente con data.source
      const feedText = document.getElementById('feed-status-text');
      const feedBadge = document.getElementById('feed-status-badge');
      if (feedText && feedBadge) {
        if (data.source === 'demo') {
          feedBadge.className = "px-2 py-0.5 rounded bg-amber-500/15 text-amber-400 font-mono text-[10px] font-bold uppercase tracking-wider inline-flex items-center gap-1";
          feedText.innerText = "Modo Demo / Sintético";
        } else {
          feedBadge.className = "px-2 py-0.5 rounded bg-tertiary/15 text-tertiary font-mono text-[10px] font-bold uppercase tracking-wider inline-flex items-center gap-1";
          feedText.innerText = "Binance Futures (OBSERVED)";
        }
      }

      // Bento stats
      let totalShortVol = 0;
      let totalLongVol = 0;
      data.bins.forEach(b => {
        totalShortVol += b.short_volume_usd;
        totalLongVol += b.long_volume_usd;
      });
      document.getElementById('tile-short-vol').innerText = `$${(totalShortVol / 1e6).toFixed(1)}M`;
      document.getElementById('tile-long-vol').innerText = `$${(totalLongVol / 1e6).toFixed(1)}M`;

      // Update Long/Short Ratio Tile with Binance live telemetry
      if (data.long_account_ratio !== undefined && data.short_account_ratio !== undefined) {
        const longPct = (data.long_account_ratio * 100).toFixed(1);
        const shortPct = (data.short_account_ratio * 100).toFixed(1);
        const elLong = document.getElementById('ratio-long-text');
        const elShort = document.getElementById('ratio-short-text');
        const barLong = document.getElementById('ratio-long-bar');
        const barShort = document.getElementById('ratio-short-bar');
        if (elLong) elLong.innerText = `${longPct}% Long`;
        if (elShort) elShort.innerText = `${shortPct}% Short`;
        if (barLong) barLong.style.width = `${longPct}%`;
        if (barShort) barShort.style.width = `${shortPct}%`;
        const pill = document.getElementById('ratio-mode-pill');
        if (pill) {
          pill.innerText = data.ratio_source === 'live' ? 'BINANCE LIVE' : (data.ratio_source === 'custom' ? 'CUSTOM' : 'NEUTRAL');
        }
      }

      // Ladder render
      const container = document.getElementById('ladder-container');
      container.innerHTML = '';

      if (!data.bins || data.bins.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-xs font-mono text-outline">No hay zonas de liquidación modeladas en el rango seleccionado.</div>`;
        return;
      }

      const maxVol = Math.max(...data.bins.map(b => b.estimated_volume_usd));
      const sortedBins = [...data.bins].sort((a, b) => b.price_min - a.price_min);
      let markPriceInserted = false;

      // Identify max magnet pool
      let maxClusterBin = sortedBins[0];
      sortedBins.forEach(b => {
        if (b.estimated_volume_usd > maxClusterBin.estimated_volume_usd) {
          maxClusterBin = b;
        }
      });
      updateMagnetCard(maxClusterBin, data.current_price);

      // Filter by selected leverage if active
      let displayBins = sortedBins;
      if (selectedLevFilter > 0) {
        displayBins = sortedBins.filter(b => b.leverages && b.leverages.includes(selectedLevFilter));
      }

      displayBins.forEach(b => {
        if (!markPriceInserted && b.price_max <= data.current_price) {
          container.appendChild(createMarkPriceLaser(data.current_price));
          markPriceInserted = true;
        }

        const isShort = b.short_volume_usd > b.long_volume_usd;
        const volPct = Math.min(100, Math.max(12, (b.estimated_volume_usd / maxVol) * 100));
        const isMax = (b.price_min === maxClusterBin.price_min);
        const levBadge = b.dominant_leverage ? `${b.dominant_leverage}x` : 'Multi';

        // Gradient styles
        const gradientClass = isShort
          ? 'bg-gradient-to-r from-secondary-container/40 via-secondary-container to-secondary-fixed-dim text-on-secondary shadow-sm'
          : 'bg-gradient-to-r from-tertiary-container/40 via-tertiary to-tertiary-fixed text-on-tertiary shadow-sm';

        const row = document.createElement('div');
        row.className = `grid grid-cols-12 items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-surface-container transition-all cursor-pointer text-xs font-mono border ${isMax ? 'border-secondary-container/50 bg-secondary-container/10 laser-glow' : 'border-transparent'}`;
        row.onclick = () => inspectBin(b, data.current_price);
        row.title = `Click para inspeccionar clúster en $${b.price_mid.toLocaleString()}`;

        row.innerHTML = `
          <div class="col-span-4 flex flex-col">
            <div class="flex items-center gap-1.5">
              <span class="text-white font-bold text-xs">$${b.price_mid.toLocaleString('en-US', { minimumFractionDigits: currentSymbol === 'ETHUSDT' ? 2 : 0 })}</span>
              ${isMax ? '<span class="px-1.5 py-0.2 rounded bg-secondary-container text-on-secondary text-[9px] font-extrabold uppercase animate-pulse flex items-center gap-0.5"><span class="material-symbols-outlined text-[10px]">local_fire_department</span>MAX LIQ</span>' : ''}
            </div>
            <span class="text-outline text-[10px]">$${b.price_min.toLocaleString()} - $${b.price_max.toLocaleString()}</span>
          </div>
          <div class="col-span-5 relative h-7 bg-surface-container-low rounded overflow-hidden flex items-center px-2">
            <div class="absolute left-0 top-0 bottom-0 ${gradientClass} rounded transition-all duration-300" style="width: ${volPct}%"></div>
            <div class="relative z-10 flex items-center justify-between w-full">
              <span class="font-extrabold text-xs drop-shadow text-white">
                $${(b.estimated_volume_usd / 1e6).toFixed(2)}M
              </span>
              <span class="px-1.5 py-0.2 rounded bg-surface-container-highest/90 border border-surface-container-high text-primary-container text-[10px] font-bold">
                ${levBadge}
              </span>
            </div>
          </div>
          <div class="col-span-3 text-right font-bold text-[11px] ${isShort ? 'text-secondary' : 'text-tertiary'} flex items-center justify-end gap-1">
            <span class="material-symbols-outlined text-[14px]">${isShort ? 'arrow_upward' : 'arrow_downward'}</span>
            <span>${isShort ? 'SHORT POOL' : 'LONG POOL'}</span>
          </div>
        `;
        container.appendChild(row);
      });

      if (!markPriceInserted) {
        container.appendChild(createMarkPriceLaser(data.current_price));
      }
    }

    // Laser Line Banner
    function createMarkPriceLaser(price) {
      const laser = document.createElement('div');
      laser.className = 'my-2 py-1 px-3 rounded bg-primary-container/20 border-y border-primary-container flex items-center justify-between text-xs font-mono font-bold text-primary-container laser-glow z-20';
      laser.innerHTML = `
        <span class="flex items-center gap-1.5 uppercase tracking-widest text-[10px]">
          <span class="w-2 h-2 rounded-full bg-primary-container animate-ping"></span>
          PRECIO MARK LIVE EN TIEMPO REAL
        </span>
        <span class="text-white text-sm font-extrabold">$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
      `;
      return laser;
    }

    // Update Magnet Cluster
    function updateMagnetCard(bin, markPrice) {
      if (!bin) return;
      const mid = bin.price_mid;
      const diffPct = ((mid - markPrice) / markPrice) * 100;
      const distUsd = Math.abs(mid - markPrice);
      const lev = bin.dominant_leverage ? `${bin.dominant_leverage}x` : '25x-50x';

      document.getElementById('magnet-price').innerText = `$${mid.toLocaleString('en-US', { minimumFractionDigits: currentSymbol === 'ETHUSDT' ? 2 : 0, maximumFractionDigits: 2 })}`;
      document.getElementById('magnet-dist').innerText = `Distancia al Mark: ${diffPct >= 0 ? '+' : ''}${diffPct.toFixed(2)}% (~$${distUsd.toFixed(2)})`;
      document.getElementById('magnet-vol').innerText = `$${(bin.estimated_volume_usd / 1e6).toFixed(1)}M`;
      const levEl = document.getElementById('magnet-lev');
      if (levEl) levEl.innerText = `Apalancamiento Dominante: ${lev}`;
    }

    function inspectCluster() {
      const panel = document.getElementById('clusterInspectionPanel');
      if (panel) panel.classList.toggle('hidden');
    }

    function inspectBin(bin, currentPrice) {
      if (!bin) return;
      const panel = document.getElementById('clusterInspectionPanel');
      if (panel) panel.classList.remove('hidden');

      const mark = currentPrice || (currentData ? currentData.current_price : 0);
      const mid = bin.price_mid;
      const diffPct = mark > 0 ? (((mid - mark) / mark) * 100) : 0;
      const lev = bin.dominant_leverage || 50;

      let mmrPct = '0.5%';
      if (lev === 5) mmrPct = '4.0%';
      else if (lev === 10) mmrPct = '2.0%';
      else if (lev === 25) mmrPct = '1.0%';
      else if (lev === 50) mmrPct = '0.5%';
      else if (lev === 100) mmrPct = '0.4%';

      const titleEl = document.getElementById('inspect-cluster-title');
      const tierEl = document.getElementById('inspect-tier');
      const deltaEl = document.getElementById('inspect-delta');
      const volEl = document.getElementById('inspect-vol');
      const riskEl = document.getElementById('inspect-risk');

      if (titleEl) titleEl.innerText = `Desglose Clúster: $${bin.price_mid.toLocaleString()} (${bin.price_min.toLocaleString()} - ${bin.price_max.toLocaleString()})`;
      if (tierEl) tierEl.innerText = `${lev}x (MMR ${mmrPct})`;
      if (deltaEl) deltaEl.innerText = `${diffPct >= 0 ? '+' : ''}${diffPct.toFixed(2)}% al Mark`;
      if (volEl) volEl.innerText = `$${(bin.estimated_volume_usd / 1e6).toFixed(2)}M`;
      if (riskEl) {
        if (Math.abs(diffPct) <= 2.0) {
          riskEl.innerText = 'CRÍTICO / INMEDIATO';
          riskEl.className = 'font-bold text-error';
        } else if (Math.abs(diffPct) <= 5.0) {
          riskEl.innerText = 'ELEVADO';
          riskEl.className = 'font-bold text-secondary-container';
        } else {
          riskEl.innerText = 'MODERADO';
          riskEl.className = 'font-bold text-primary';
        }
      }
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function closeInspection() {
      const panel = document.getElementById('clusterInspectionPanel');
      if (panel) panel.classList.add('hidden');
    }

    // Update Model & Data tab
    function updateModelView(data) {
      const p = `$${data.current_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      const oi = `~$${(data.total_open_interest_usd / 1e6).toFixed(1)}M`;
      const elP = document.getElementById('model-mark-display');
      const elOI = document.getElementById('model-oi-display');
      if (elP) elP.innerText = p;
      if (elOI) elOI.innerText = oi;
    }

    // Simulator Functions
    function updateSimulatorFromData(data) {
      const simRef = document.getElementById('sim-ref-mark');
      if (simRef) simRef.innerText = `$${data.current_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }

    function setSimDirection(dir) {
      simDirection = dir;
      const btnL = document.getElementById('sim-btn-long');
      const btnS = document.getElementById('sim-btn-short');
      if (dir === 'LONG') {
        btnL.className = 'py-2 px-3 rounded font-mono text-xs font-bold transition-all bg-tertiary-container text-on-tertiary flex items-center justify-center gap-1.5';
        btnS.className = 'py-2 px-3 rounded font-mono text-xs font-bold transition-all text-on-surface-variant hover:text-white flex items-center justify-center gap-1.5';
      } else {
        btnS.className = 'py-2 px-3 rounded font-mono text-xs font-bold transition-all bg-secondary-container text-on-secondary flex items-center justify-center gap-1.5';
        btnL.className = 'py-2 px-3 rounded font-mono text-xs font-bold transition-all text-on-surface-variant hover:text-white flex items-center justify-center gap-1.5';
      }
      recalcSimulator();
    }

    function setSimLeverage(lev, mmr) {
      simLeverage = lev;
      simMMR = mmr;
      document.getElementById('sim-lev-label').innerText = `${lev}x Multiplier (MMR ${(mmr * 100).toFixed(1)}%)`;

      const btns = document.querySelectorAll('#sim-leverage-buttons .sim-lev');
      const levs = [5, 10, 25, 50, 100];
      btns.forEach((b, idx) => {
        if (levs[idx] === lev) {
          b.className = 'sim-lev py-2 rounded bg-primary-container text-on-primary-container font-mono text-xs font-bold shadow transition-colors';
        } else {
          b.className = 'sim-lev py-2 rounded bg-surface-container-low hover:bg-surface-container-high text-outline hover:text-white font-mono text-xs font-bold transition-colors';
        }
      });
      recalcSimulator();
    }

    function useMarkInSim() {
      if (currentData) {
        document.getElementById('sim-entry-input').value = Math.round(currentData.current_price);
        recalcSimulator();
      }
    }

    function recalcSimulator() {
      const entryPrice = parseFloat(document.getElementById('sim-entry-input').value) || 81420;
      let liqPrice = 0;
      let distPct = 0;

      if (simDirection === 'LONG') {
        // Long Liq: Entry * (1 - 1/Lev + MMR)
        liqPrice = entryPrice * (1.0 - (1.0 / simLeverage) + simMMR);
        distPct = ((liqPrice - entryPrice) / entryPrice) * 100;
      } else {
        // Short Liq: Entry * (1 + 1/Lev - MMR)
        liqPrice = entryPrice * (1.0 + (1.0 / simLeverage) - simMMR);
        distPct = ((liqPrice - entryPrice) / entryPrice) * 100;
      }

      const bufferUsd = Math.abs(entryPrice - liqPrice);
      document.getElementById('sim-liq-result').innerText = `$${liqPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      document.getElementById('sim-dist-result').innerText = `${distPct >= 0 ? '+' : ''}${distPct.toFixed(2)}%`;
      document.getElementById('sim-mmr-badge').innerText = `${(simMMR * 100).toFixed(2)}%`;
      document.getElementById('sim-buffer-badge').innerText = `~$${bufferUsd.toLocaleString('en-US', { minimumFractionDigits: 2 })} USDT`;
    }

    // Check hash for direct tab linking (e.g. #manual)
    if (window.location.hash === '#manual') {
      switchTab('manual');
    }

    // Initial Start
    fetchHeatmap(true);
    startAutoRefreshTimer();
    recalcSimulator();
  </script>

</body>
</html>
"""


def get_dashboard_html() -> str:
    """Retorna el contenido HTML del visualizador de mapa de calor interactivo."""
    return DASHBOARD_HTML
