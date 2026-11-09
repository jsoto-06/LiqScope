"""Plantilla y generador del Dashboard HTML interactivo para LiqScope.

Incorpora el sistema de diseño institucional 'OLED Deep Heat Terminal' con:
- Paleta de alta densidad cyber-financiera (OLED Obsidian, Cyan Mark, Emerald Longs, Crimson Shorts, Solar Gold).
- Tipografía Inter (estructural) y JetBrains Mono (cuantitativa/telemetría con tabular nums).
- Iconografía Google Material Symbols Outlined.
- Navegación multi-pestaña dual: tabs integradas en cabecera para PC y barra inferior táctil para móviles.
- Gráfico de perfil de profundidad de liquidaciones (Visual Liquidation Profile Chart) y Escalera DOM Pro.
- Manual exhaustivo de usuario y guía técnica paso a paso integrada.
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

  <!-- TradingView Lightweight Charts CDN -->
  <script src="https://cdn.jsdelivr.net/npm/lightweight-charts@4.2.1/dist/lightweight-charts.standalone.production.js"></script>
  <script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            "surface": "#07090e",
            "surface-dim": "#07090e",
            "surface-panel": "#0d111a",
            "surface-card": "#111624",
            "surface-card-high": "#161d2f",
            "surface-border": "#1b253b",
            "surface-border-subtle": "#141c2c",
            "on-surface": "#e2e6f0",
            "on-surface-variant": "#8e9bb5",
            "outline": "#657594",
            "mark": "#00e5ff",
            "mark-subtle": "rgba(0, 229, 255, 0.15)",
            "short": "#ff3358",
            "short-subtle": "rgba(255, 51, 88, 0.15)",
            "long": "#00f090",
            "long-subtle": "rgba(0, 240, 144, 0.15)",
            "magnet": "#ffb800",
            "magnet-subtle": "rgba(255, 184, 0, 0.15)",
            "primary": "#a5e7ff",
            "primary-container": "#00e5ff",
            "on-primary-container": "#003543",
            "secondary": "#ffb800",
            "secondary-container": "#ffb800",
            "secondary-fixed-dim": "#e0a200",
            "tertiary": "#00f090",
            "tertiary-container": "#00f090",
            "error": "#ff3358"
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
      background-color: #07090e;
      color: #e2e6f0;
      font-family: 'Inter', system-ui, sans-serif;
      overflow-x: hidden;
      -webkit-tap-highlight-color: transparent;
    }
    .font-mono {
      font-family: 'JetBrains Mono', monospace;
      font-feature-settings: "tnum" 1;
      font-variant-numeric: tabular-nums;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 4px;
      height: 4px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: #07090e;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: #1b253b;
      border-radius: 4px;
    }
    .laser-glow {
      box-shadow: 0 0 16px rgba(0, 229, 255, 0.45);
    }
    .magnet-glow {
      box-shadow: 0 0 18px rgba(255, 184, 0, 0.35);
    }
    .short-glow {
      box-shadow: 0 0 12px rgba(255, 51, 88, 0.35);
    }
    .long-glow {
      box-shadow: 0 0 12px rgba(0, 240, 144, 0.35);
    }
    .no-scrollbar::-webkit-scrollbar {
      display: none;
    }
    .no-scrollbar {
      -ms-overflow-style: none;
      scrollbar-width: none;
    }
  </style>
</head>

<body class="bg-surface text-on-surface antialiased flex flex-col min-h-screen selection:bg-mark/20 selection:text-mark pb-24 md:pb-8">

  <!-- TOP HIGH-DENSITY INSTITUTIONAL TELEMETRY HEADER -->
  <header class="fixed top-0 inset-x-0 z-50 bg-[#07090e]/95 backdrop-blur-xl border-b border-surface-border shadow-2xl">
    <div class="max-w-7xl mx-auto px-3 sm:px-4 h-12 sm:h-13 flex items-center justify-between gap-2 sm:gap-4">

      <!-- Left: Brand & Symbol Selector & Live Indicator -->
      <div class="flex items-center gap-2 sm:gap-3 shrink-0">
        <div class="flex items-center gap-1.5 cursor-pointer" onclick="switchTab('mapa-de-calor')">
          <div class="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-surface-card border border-mark/30 flex items-center justify-center text-mark shadow-xs">
            <span class="material-symbols-outlined text-[18px] sm:text-[20px]">radar</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="font-extrabold text-sm sm:text-base tracking-tight text-white">LiqScope</span>
            <span class="px-1.5 py-0.2 bg-mark/15 text-mark text-[9px] font-mono font-bold rounded uppercase border border-mark/25 hidden xs:inline">Pro</span>
          </div>
        </div>

        <!-- Pair Toggle (BTC / ETH) -->
        <div class="inline-flex rounded-lg border border-surface-border p-0.5 bg-surface-panel">
          <button id="btn-btc" onclick="selectSymbol('BTCUSDT')" class="px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded bg-mark text-black shadow transition-all cursor-pointer">BTC</button>
          <button id="btn-eth" onclick="selectSymbol('ETHUSDT')" class="px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer">ETH</button>
        </div>

        <!-- Live Feed Indicator (Demo hidden per user preference) -->
        <div class="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-mono font-bold rounded-lg bg-long/15 text-long border border-long/25 shadow-xs">
          <span class="w-2 h-2 rounded-full bg-long animate-pulse"></span>
          <span class="tracking-wide hidden xs:inline">BINANCE LIVE</span>
          <span class="tracking-wide xs:hidden">LIVE</span>
        </div>
        <!-- Hidden buttons to maintain JS / test invariant compatibility -->
        <button id="btn-live" onclick="setSource('live')" class="hidden">Live</button>
        <button id="btn-demo" onclick="setSource('demo')" class="hidden">Demo</button>
      </div>

      <!-- Center: Desktop Integrated Navigation Tabs (Hidden on mobile) -->
      <nav class="hidden md:flex items-center gap-1">
        <button onclick="switchTab('mapa-de-calor')" id="top-nav-mapa-de-calor" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-bold font-mono text-mark bg-surface-card border border-mark/30 transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px]">local_fire_department</span>
          <span>Mapa Calor</span>
        </button>
        <button onclick="switchTab('rekt-ticker')" id="top-nav-rekt-ticker" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer relative">
          <span class="material-symbols-outlined text-[16px] text-short animate-pulse">flash_on</span>
          <span>REKT Live</span>
          <span class="w-1.5 h-1.5 rounded-full bg-short animate-ping"></span>
        </button>
        <button onclick="switchTab('financiacion')" id="top-nav-financiacion" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px] text-cyan-400">percent</span>
          <span>Financiación</span>
          <span id="top-funding-pill" class="px-1.5 py-0.2 rounded bg-cyan-500/20 text-cyan-300 text-[9px] font-mono font-bold">+0.01%</span>
        </button>
        <button onclick="switchTab('screener')" id="top-nav-screener" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px] text-yellow-400">military_tech</span>
          <span>Ganadoras & Ballenas</span>
        </button>
        <button onclick="switchTab('etfs')" id="top-nav-etfs" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px] text-emerald-400">account_balance</span>
          <span>ETFs Cripto</span>
        </button>
        <button onclick="switchTab('modelo-datos')" id="top-nav-modelo-datos" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px]">dataset</span>
          <span>Modelo & Datos</span>
        </button>
        <button onclick="switchTab('niveles-mmr')" id="top-nav-niveles-mmr" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px]">functions</span>
          <span>Simulador MMR</span>
        </button>
        <button onclick="switchTab('alertas')" id="top-nav-alertas" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer relative">
          <span class="material-symbols-outlined text-[16px]">notifications</span>
          <span>Alertas</span>
          <span id="top-alert-badge" class="hidden px-1.5 py-0.2 rounded-full bg-short text-white text-[9px] font-mono font-bold animate-pulse">0</span>
        </button>
        <button onclick="switchTab('manual')" id="top-nav-manual" class="top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer">
          <span class="material-symbols-outlined text-[16px]">menu_book</span>
          <span>Manual de Usuario</span>
        </button>
      </nav>

      <!-- Right: Real-Time Mark Ticker & 2-Min Countdown -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Live Mark Indicator -->
        <div class="flex flex-col items-end">
          <span class="text-[9px] font-mono text-outline uppercase tracking-wider hidden xs:block">Mark Price (Binance)</span>
          <div class="flex items-center gap-1.5">
            <span id="header-mark-price" class="text-sm sm:text-base font-mono font-black text-mark tracking-tight">$81,420.50</span>
            <span class="w-2 h-2 rounded-full bg-mark animate-ping"></span>
          </div>
        </div>

        <!-- 2-min Countdown badge -->
        <div class="flex items-center gap-1 px-2 py-1 rounded-lg border border-surface-border bg-surface-panel" title="Auto-actualización cada 2 minutos (120 s)">
          <span id="countdown-text" class="text-xs font-mono font-bold text-long">02:00</span>
          <button onclick="fetchHeatmap(true)" class="text-outline hover:text-mark transition-colors cursor-pointer ml-1" title="Actualizar ahora">
            <span class="material-symbols-outlined text-[16px]">refresh</span>
          </button>
        </div>

        <!-- Mobile badge for test invariant compatibility -->
        <span id="header-feed-badge-mob" class="hidden">LIVE</span>
        <span id="countdown-text-mob" class="hidden">02:00</span>
      </div>

    </div>
  </header>

  <!-- MAIN VIEWPORT CONTAINER -->
  <main class="max-w-7xl mx-auto px-3 sm:px-4 pt-16 sm:pt-18 w-full flex flex-col space-y-3 sm:space-y-4">

    <!-- TAB 1: MAPA DE CALOR (HEATMAP TELEMETRY) -->
    <div id="tab-mapa-de-calor" class="tab-pane flex flex-col space-y-3 sm:space-y-4">

      <!-- TOP TELEMETRY RIBBON (High density single bar) -->
      <div class="w-full bg-surface-panel border border-surface-border rounded-xl p-2.5 sm:p-3 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
        <!-- Symbol & Source badge -->
        <div class="flex items-center gap-2 flex-wrap">
          <span id="hero-symbol-badge" class="font-mono text-xs sm:text-sm font-bold text-white flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-mark"></span>
            BTC/USDT USDⓈ-M
          </span>
          <span id="feed-status-badge" class="px-2 py-0.5 rounded bg-long/15 text-long font-mono text-[10px] font-bold uppercase flex items-center gap-1 border border-long/25">
            <span class="material-symbols-outlined text-[12px]">verified</span>
            <span id="feed-status-text">Binance 100% Real</span>
          </span>
          <span id="sync-time-badge" class="text-[10px] font-mono text-outline ml-auto sm:ml-2">Sinc: --:--:--</span>
        </div>

        <!-- Telemetry Stats Strip -->
        <div class="flex items-center justify-between sm:justify-end gap-3 sm:gap-6 bg-surface/80 rounded-lg px-3 py-1.5 border border-surface-border-subtle font-mono text-xs">
          <div class="flex flex-col">
            <span class="text-[9px] text-outline uppercase tracking-wider">Open Interest</span>
            <span id="metric-oi-usd" class="text-white font-bold">$7,742.85M <span class="text-outline text-[10px]">USD</span></span>
          </div>
          <div class="flex flex-col items-end sm:items-start">
            <span class="text-[9px] text-outline uppercase tracking-wider">Volumen Cripto</span>
            <span id="metric-oi-coins" class="text-mark font-bold">~95,120 BTC</span>
          </div>
          <div class="flex flex-col items-end sm:items-start">
            <span class="text-[9px] text-outline uppercase tracking-wider">Funding Rate</span>
            <span id="metric-funding-rate" class="text-cyan-400 font-bold">+0.0100% <span class="text-outline text-[10px]">8h</span></span>
          </div>
          <div class="flex flex-col items-end">
            <span class="text-[9px] text-outline uppercase tracking-wider">Cobertura</span>
            <span id="coverage-badge" class="text-long font-bold">100.0%</span>
          </div>
        </div>
      </div>

      <!-- MULTI-EXCHANGE SELECTOR & LIQUIDITY DISTRIBUTION BAR -->
      <div class="w-full bg-surface-panel border border-surface-border rounded-xl p-3 shadow-md flex flex-col space-y-2.5">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-mark text-[18px]">public</span>
            <span class="font-mono text-xs font-bold text-white uppercase tracking-wider">Agregación Multi-Exchange</span>
            <span id="active-exchange-pill" class="px-2 py-0.5 rounded bg-mark/15 text-mark font-mono text-[9px] font-bold border border-mark/25">GLOBAL 4 EXCHANGES</span>
          </div>

          <!-- Exchange Selector Buttons -->
          <div class="inline-flex rounded-lg border border-surface-border p-0.5 bg-surface gap-0.5 flex-wrap">
            <button id="btn-ex-all" onclick="selectExchange('all')" class="px-2.5 py-1 text-xs font-mono font-bold rounded bg-mark text-black transition-all cursor-pointer shadow">🌐 Global (Todos)</button>
            <button id="btn-ex-binance" onclick="selectExchange('binance')" class="px-2.5 py-1 text-xs font-mono font-bold rounded text-outline hover:text-white transition-all cursor-pointer">🟡 Binance</button>
            <button id="btn-ex-bybit" onclick="selectExchange('bybit')" class="px-2.5 py-1 text-xs font-mono font-bold rounded text-outline hover:text-white transition-all cursor-pointer">🟠 Bybit</button>
            <button id="btn-ex-hyperliquid" onclick="selectExchange('hyperliquid')" class="px-2.5 py-1 text-xs font-mono font-bold rounded text-outline hover:text-white transition-all cursor-pointer">🟢 Hyperliquid</button>
            <button id="btn-ex-kraken" onclick="selectExchange('kraken')" class="px-2.5 py-1 text-xs font-mono font-bold rounded text-outline hover:text-white transition-all cursor-pointer">🟣 Kraken</button>
          </div>
        </div>

        <!-- Visual Multi-Exchange Open Interest Distribution Progress Bar -->
        <div class="flex flex-col space-y-1 pt-1 border-t border-surface-border-subtle">
          <div class="flex items-center justify-between text-[10px] font-mono text-outline">
            <span>Cuota de Open Interest Nocional:</span>
            <span id="exchange-total-oi-badge" class="text-white font-bold">$15,820M USD Total Agregado</span>
          </div>
          <div class="w-full h-2 rounded-full bg-surface overflow-hidden flex" id="exchange-distribution-bar">
            <div id="bar-binance" class="bg-amber-400 h-full transition-all duration-300" style="width: 46%" title="Binance Futures"></div>
            <div id="bar-bybit" class="bg-orange-500 h-full transition-all duration-300" style="width: 33%" title="Bybit Linear"></div>
            <div id="bar-hyperliquid" class="bg-emerald-400 h-full transition-all duration-300" style="width: 20%" title="Hyperliquid DEX"></div>
            <div id="bar-kraken" class="bg-purple-500 h-full transition-all duration-300" style="width: 1%" title="Kraken Futures"></div>
          </div>
          <div class="flex items-center justify-between text-[9px] font-mono pt-0.5 flex-wrap gap-2 text-outline" id="exchange-legend">
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-amber-400"></span> Binance: <strong id="val-binance" class="text-white">--</strong></span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-orange-500"></span> Bybit: <strong id="val-bybit" class="text-white">--</strong></span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-emerald-400"></span> Hyperliquid: <strong id="val-hyperliquid" class="text-white">--</strong></span>
            <span class="flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-purple-500"></span> Kraken: <strong id="val-kraken" class="text-white">--</strong></span>
          </div>
        </div>
      </div>

      <!-- LIVE REKT TICKER RIBBON -->
      <div class="w-full bg-surface-panel border border-surface-border rounded-xl px-3 py-2 shadow-md flex items-center justify-between gap-3 overflow-hidden cursor-pointer hover:border-mark/40 transition-all group" onclick="switchTab('rekt-ticker')" title="Abrir terminal de liquidaciones en directo">
        <div class="flex items-center gap-2 shrink-0">
          <span class="flex h-2 w-2 relative">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-short opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-short"></span>
          </span>
          <span class="font-mono text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1">
            <span class="text-short font-black">REKT</span> LIVE:
          </span>
        </div>
        <div id="rekt-tape-container" class="flex-1 overflow-hidden whitespace-nowrap text-xs font-mono text-outline flex items-center gap-3">
          <span class="text-outline text-xs animate-pulse">Conectando al stream en vivo de Binance forceOrders...</span>
        </div>
        <div class="shrink-0 flex items-center gap-1 text-[11px] font-mono text-mark bg-mark/10 px-2 py-0.5 rounded border border-mark/20 group-hover:bg-mark group-hover:text-black transition-all">
          <span>Abrir Ticker</span>
          <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
        </div>
      </div>

      <!-- MAIN PRO WORKSPACE: 2-COLUMN DESKTOP / FLUID MOBILE -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-3 sm:gap-4 items-start">

        <!-- LEFT COLUMN (PC: 4 cols / 33%) -> Analytics, Risk, Magnet & Quick Simulator -->
        <div class="lg:col-span-4 flex flex-col space-y-3 sm:space-y-3.5 order-2 lg:order-1">

          <!-- 1. ZONA DE MAYOR MAGNETISMO (EPICENTER CLUSTER) -->
          <div class="bg-surface-panel border border-surface-border rounded-xl p-3 sm:p-4 shadow-md flex flex-col gap-2 relative overflow-hidden">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <span class="material-symbols-outlined text-magnet text-[20px]">attractions</span>
                <span class="text-xs sm:text-sm font-bold text-white tracking-tight">Foco de Atracción Magnética</span>
              </div>
              <span class="px-2 py-0.5 rounded bg-magnet/20 text-magnet font-mono text-[9px] font-bold uppercase border border-magnet/30 animate-pulse">
                MAX LIQ POOL
              </span>
            </div>

            <div class="flex items-baseline justify-between pt-1 border-t border-surface-border-subtle">
              <div class="flex flex-col">
                <span id="magnet-price" class="font-mono text-xl sm:text-2xl text-magnet font-extrabold tracking-tight">$83,000</span>
                <span id="magnet-dist" class="font-mono text-[11px] text-outline font-semibold">Distancia: +1.84% (~$1,500.00)</span>
              </div>
              <div class="flex flex-col items-end">
                <span id="magnet-vol" class="font-mono text-base sm:text-lg text-white font-extrabold">$1,140.2M</span>
                <span id="magnet-lev" class="font-mono text-[10px] text-long uppercase font-bold">Apal. 25x-50x</span>
              </div>
            </div>

            <p class="text-[11px] text-on-surface-variant leading-relaxed">
              Mayor acumulación de órdenes forzadas. Probabilidad elevada de barrida algorítmica si el precio quiebra el rango actual.
            </p>

            <!-- Interactive Inspector Button -->
            <button class="mt-1 w-full py-2 bg-surface-card hover:bg-surface-card-high border border-surface-border text-mark transition-all rounded-lg font-bold text-xs flex items-center justify-center gap-1.5 shadow-sm cursor-pointer" id="inspectClusterBtn" onclick="inspectCluster()">
              <span class="material-symbols-outlined text-[16px]">travel_explore</span>
              <span>Inspeccionar Desglose Institucional</span>
            </button>

            <!-- Inspection Drawer Panel -->
            <div class="hidden w-full bg-surface-card rounded-lg p-2.5 flex-col gap-2 border border-surface-border mt-1.5" id="clusterInspectionPanel">
              <div class="flex items-center justify-between pb-1 border-b border-surface-border">
                <span id="inspect-cluster-title" class="text-[11px] font-bold text-white font-mono truncate">Desglose del Clúster</span>
                <button onclick="closeInspection()" class="text-outline hover:text-white text-xs font-mono cursor-pointer ml-1">×</button>
              </div>
              <div class="grid grid-cols-2 gap-1.5 pt-1 font-mono text-[11px]">
                <div class="bg-surface p-1.5 rounded">
                  <span class="text-outline text-[9px] block">Apalancamiento</span>
                  <span id="inspect-tier" class="font-bold text-white">25x (MMR 1.0%)</span>
                </div>
                <div class="bg-surface p-1.5 rounded">
                  <span class="text-outline text-[9px] block">Delta Requerido</span>
                  <span id="inspect-delta" class="font-bold text-magnet">3.00%</span>
                </div>
                <div class="bg-surface p-1.5 rounded">
                  <span class="text-outline text-[9px] block">Volumen Estimado</span>
                  <span id="inspect-vol" class="font-bold text-mark">$1,140.2M</span>
                </div>
                <div class="bg-surface p-1.5 rounded">
                  <span class="text-outline text-[9px] block">Riesgo Cascada</span>
                  <span id="inspect-risk" class="font-bold text-short">ELEVADO</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 2. SUMMARY RISK METRICS (Shorts, Longs, Ratio L/S) -->
          <div class="bg-surface-panel border border-surface-border rounded-xl p-3 sm:p-4 shadow-sm space-y-3">
            <span class="text-xs font-bold text-white uppercase tracking-wider block">Telemetría de Riesgo de Mercado</span>

            <!-- Long / Short Ratio Bar Tile -->
            <div class="space-y-1">
              <div class="flex items-center justify-between text-xs font-mono">
                <span class="text-[11px] text-on-surface-variant flex items-center gap-1">
                  Ratio Cuentas L/S
                  <span id="ratio-mode-pill" class="text-[8px] font-bold px-1 py-0.2 rounded bg-long/15 text-long border border-long/20">LIVE</span>
                </span>
                <div class="flex items-center gap-1.5 font-bold">
                  <span id="ratio-long-text" class="text-long">50.0% L</span>
                  <span class="text-outline">/</span>
                  <span id="ratio-short-text" class="text-short">50.0% S</span>
                </div>
              </div>
              <!-- Dual Segment Bar -->
              <div class="w-full h-2 rounded-full bg-surface overflow-hidden flex border border-surface-border">
                <div id="ratio-long-bar" class="h-full bg-long transition-all duration-500" style="width: 50%"></div>
                <div id="ratio-short-bar" class="h-full bg-short transition-all duration-500" style="width: 50%"></div>
              </div>
            </div>

            <!-- Exposed Volume Blocks -->
            <div class="grid grid-cols-2 gap-2 pt-1 font-mono">
              <div class="bg-surface p-2.5 rounded-lg border border-short/20 flex flex-col justify-between">
                <div class="flex items-center gap-1 text-[10px] text-short font-bold">
                  <span class="material-symbols-outlined text-[13px]">arrow_circle_up</span>
                  <span>Shorts en Riesgo</span>
                </div>
                <span id="tile-short-vol" class="text-sm sm:text-base font-black text-white mt-1">$3,871.4M</span>
                <span class="text-[9px] text-outline">Barrida alcista</span>
              </div>

              <div class="bg-surface p-2.5 rounded-lg border border-long/20 flex flex-col justify-between">
                <div class="flex items-center gap-1 text-[10px] text-long font-bold">
                  <span class="material-symbols-outlined text-[13px]">arrow_circle_down</span>
                  <span>Longs en Riesgo</span>
                </div>
                <span id="tile-long-vol" class="text-sm sm:text-base font-black text-white mt-1">$3,871.4M</span>
                <span class="text-[9px] text-outline">Soporte dinámico</span>
              </div>
            </div>
          </div>

          <!-- 3. MINI-SIMULADOR RÁPIDO (Always available on PC) -->
          <div class="bg-surface-panel border border-surface-border rounded-xl p-3 sm:p-4 shadow-sm space-y-2.5">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-1.5">
                <span class="material-symbols-outlined text-mark text-[18px]">calculate</span>
                <span class="text-xs font-bold text-white">Simulador MMR Rápido</span>
              </div>
              <button onclick="useMarkInSim()" class="text-mark font-mono text-[10px] hover:underline flex items-center gap-0.5 cursor-pointer">
                <span class="material-symbols-outlined text-[12px]">bolt</span>Usar Mark
              </button>
            </div>

            <!-- Direction Toggle -->
            <div class="grid grid-cols-2 gap-1.5 p-0.5 rounded-lg bg-surface border border-surface-border font-mono text-xs">
              <button id="sim-btn-long" onclick="setSimDirection('LONG')" class="py-1 rounded font-bold transition-all bg-long text-black flex items-center justify-center gap-1 cursor-pointer">
                <span>LONG</span>
              </button>
              <button id="sim-btn-short" onclick="setSimDirection('SHORT')" class="py-1 rounded font-bold transition-all text-on-surface-variant hover:text-white flex items-center justify-center gap-1 cursor-pointer">
                <span>SHORT</span>
              </button>
            </div>

            <!-- Input & Leverage row -->
            <div class="grid grid-cols-2 gap-2 font-mono text-xs">
              <div class="bg-surface px-2.5 py-1.5 rounded-lg border border-surface-border flex items-center">
                <span class="text-outline mr-1">$</span>
                <input id="sim-entry-input" type="number" value="81420" oninput="recalcSimulator()" class="w-full bg-transparent font-bold text-white focus:outline-none">
              </div>
              <div class="grid grid-cols-5 gap-1" id="sim-leverage-buttons">
                <button onclick="setSimLeverage(5, 0.04)" class="sim-lev py-1 rounded bg-surface hover:bg-surface-card text-outline hover:text-white text-[10px] font-bold transition-colors cursor-pointer">5x</button>
                <button onclick="setSimLeverage(10, 0.02)" class="sim-lev py-1 rounded bg-surface hover:bg-surface-card text-outline hover:text-white text-[10px] font-bold transition-colors cursor-pointer">10x</button>
                <button onclick="setSimLeverage(25, 0.01)" class="sim-lev py-1 rounded bg-surface hover:bg-surface-card text-outline hover:text-white text-[10px] font-bold transition-colors cursor-pointer">25x</button>
                <button onclick="setSimLeverage(50, 0.005)" class="sim-lev py-1 rounded bg-mark text-black text-[10px] font-bold transition-colors cursor-pointer">50x</button>
                <button onclick="setSimLeverage(100, 0.004)" class="sim-lev py-1 rounded bg-surface hover:bg-surface-card text-outline hover:text-white text-[10px] font-bold transition-colors cursor-pointer">100x</button>
              </div>
            </div>

            <!-- Output block -->
            <div class="bg-surface rounded-lg p-2.5 border border-surface-border flex items-center justify-between font-mono">
              <div>
                <span class="text-[9px] text-outline uppercase block">Precio Liquidación</span>
                <span id="sim-liq-result" class="text-base font-extrabold text-long">$80,198.70</span>
              </div>
              <div class="text-right">
                <span class="text-[9px] text-outline uppercase block">Distancia</span>
                <span id="sim-dist-result" class="text-xs font-bold text-magnet">-1.50%</span>
              </div>
            </div>
            <span id="sim-lev-label" class="hidden">50x Multiplier (MMR 0.5%)</span>
            <span id="sim-mmr-badge" class="hidden">0.50%</span>
            <span id="sim-buffer-badge" class="hidden">~$1,221.80 USDT</span>
            <span id="sim-ref-mark" class="hidden">$81,420.50</span>
          </div>

        </div>

        <!-- RIGHT COLUMN (PC: 8 cols / 67%) -> Liquidation Profile & Heatmap Matrix -->
        <div class="lg:col-span-8 flex flex-col space-y-3 order-1 lg:order-2">

          <!-- Controls Bar (Granular Bins, Min/Max Range & Quick Leverage Chips) -->
          <div class="bg-surface-panel border border-surface-border p-2.5 sm:p-3 rounded-xl flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 shadow-xs">

            <!-- Granularity, Horizon & Range Inputs -->
            <div class="flex items-center gap-2 flex-wrap">
              <!-- LiqScope Horizon Selector -->
              <div class="flex items-center gap-1 text-xs font-mono text-outline">
                <span class="material-symbols-outlined text-[15px] text-mark">schedule</span>
                <span class="text-[10px] uppercase font-bold hidden sm:inline">Horizonte:</span>
              </div>
              <select id="select-timeframe-horizon" onchange="changeTimeframeHorizon(this.value)" class="px-2.5 py-1 text-xs font-mono font-bold rounded-lg bg-surface border border-surface-border text-mark focus:outline-none focus:border-mark cursor-pointer" title="Horizonte temporal de acumulación de posiciones LiqScope">
                <option value="12h">⏱️ 12 Horas</option>
                <option value="24h" selected>⏱️ 24 Horas</option>
                <option value="3d">⏱️ 3 Días</option>
                <option value="1w">⏱️ 1 Semana</option>
                <option value="1m">⏱️ 1 Mes</option>
                <option value="3m">⏱️ 3 Meses</option>
              </select>

              <div class="flex items-center gap-1 text-xs font-mono text-outline ml-1">
                <span class="material-symbols-outlined text-[15px] text-mark">tune</span>
                <span class="text-[10px] uppercase font-bold">Bins:</span>
              </div>
              <select id="select-bin-size" onchange="fetchHeatmap(true)" class="px-2.5 py-1 text-xs font-mono font-bold rounded-lg bg-surface border border-surface-border text-white focus:outline-none focus:border-mark cursor-pointer">
                <option value="10">10 USD (ETH)</option>
                <option value="25">25 USD</option>
                <option value="50" selected>50 USD (BTC)</option>
                <option value="100">100 USD</option>
                <option value="250">250 USD</option>
                <option value="500">500 USD</option>
              </select>

              <input type="number" id="input-min" placeholder="Min $" onchange="fetchHeatmap(true)" class="w-20 px-2 py-1 text-xs font-mono rounded-lg bg-surface border border-surface-border text-white placeholder-slate-500">
              <input type="number" id="input-max" placeholder="Max $" onchange="fetchHeatmap(true)" class="w-20 px-2 py-1 text-xs font-mono rounded-lg bg-surface border border-surface-border text-white placeholder-slate-500">
              <button onclick="resetFilters()" class="text-xs font-mono text-outline hover:text-mark px-1 cursor-pointer" title="Restablecer">Reset</button>
            </div>

            <!-- Leverage Filter Chips -->
            <div class="flex items-center gap-1 overflow-x-auto no-scrollbar py-0.5" id="leverageChips">
              <button onclick="filterByLeverage(0)" class="lev-chip px-2.5 py-1 rounded-lg bg-mark text-black font-mono text-[11px] font-bold transition-all shadow-xs cursor-pointer">Todos</button>
              <button onclick="filterByLeverage(5)" class="lev-chip px-2.5 py-1 rounded-lg bg-surface text-outline hover:text-white font-mono text-[11px] font-semibold transition-all cursor-pointer">5x</button>
              <button onclick="filterByLeverage(10)" class="lev-chip px-2.5 py-1 rounded-lg bg-surface text-outline hover:text-white font-mono text-[11px] font-semibold transition-all cursor-pointer">10x</button>
              <button onclick="filterByLeverage(25)" class="lev-chip px-2.5 py-1 rounded-lg bg-surface text-outline hover:text-white font-mono text-[11px] font-semibold transition-all cursor-pointer">25x</button>
              <button onclick="filterByLeverage(50)" class="lev-chip px-2.5 py-1 rounded-lg bg-surface text-outline hover:text-white font-mono text-[11px] font-semibold transition-all cursor-pointer">50x</button>
              <button onclick="filterByLeverage(100)" class="lev-chip px-2.5 py-1 rounded-lg bg-surface text-outline hover:text-white font-mono text-[11px] font-semibold transition-all cursor-pointer flex items-center gap-0.5">
                <span class="material-symbols-outlined text-[12px] text-magnet">bolt</span>100x
              </button>
            </div>

          </div>

          <!-- PRIMARY HEATMAP / DOM VISUALIZER CARD -->
          <div class="w-full bg-surface-panel border border-surface-border rounded-xl p-3 sm:p-4 shadow-xl flex flex-col gap-3 relative overflow-hidden">

            <!-- Card Header: HUD & Visualizer Mode Switcher -->
            <div class="flex items-center justify-between border-b border-surface-border pb-2.5 flex-wrap gap-2">
              <div class="flex items-center gap-2">
                <span class="text-xs sm:text-sm font-bold text-white flex items-center gap-1.5 font-mono">
                  <span class="material-symbols-outlined text-mark text-[18px]">equalizer</span>
                  <span>Matriz de Liquidación</span>
                </span>
                <span id="visible-vol-badge" class="font-mono text-[11px] text-outline hidden sm:inline">Volumen: $7,742M</span>
              </div>

              <!-- View Switcher (Depth Chart vs DOM Ladder) & Legend -->
              <div class="flex items-center gap-3">
                <!-- Color Legend -->
                <div class="flex items-center gap-2.5 text-[10px] sm:text-[11px] font-mono">
                  <span class="flex items-center gap-1 text-short font-bold">
                    <span class="w-2 h-2 rounded-full bg-short"></span> Shorts
                  </span>
                  <span class="flex items-center gap-1 text-long font-bold">
                    <span class="w-2 h-2 rounded-full bg-long"></span> Longs
                  </span>
                </div>

                <!-- Mode Toggle (TradingView Velas vs Perfil vs Escalera) -->
                <div class="flex items-center p-0.5 bg-surface rounded-lg border border-surface-border gap-0.5">
                  <button id="view-mode-tv" onclick="setViewMode('tv')" class="px-2.5 py-1 rounded text-xs font-mono font-bold transition-all text-mark bg-surface-card border border-mark/25 flex items-center gap-1 cursor-pointer shadow-xs" title="Velas TradingView con Capas de Liquidación">
                    <span class="material-symbols-outlined text-[15px]">candlestick_chart</span>
                    <span>Velas Pro</span>
                  </button>
                  <button id="view-mode-chart" onclick="setViewMode('chart')" class="px-2 py-1 rounded text-xs font-mono font-semibold transition-all text-outline hover:text-white flex items-center gap-1 cursor-pointer" title="Gráfico de Perfil Horizontal">
                    <span class="material-symbols-outlined text-[14px]">align_horizontal_left</span>
                    <span class="hidden sm:inline">Perfil</span>
                  </button>
                  <button id="view-mode-ladder" onclick="setViewMode('ladder')" class="px-2 py-1 rounded text-xs font-mono font-semibold transition-all text-outline hover:text-white flex items-center gap-1 cursor-pointer" title="Escalera DOM Tradicional">
                    <span class="material-symbols-outlined text-[14px]">table_rows</span>
                    <span class="hidden sm:inline">Escalera</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- VIEW 1: TRADINGVIEW LIGHTWEIGHT CHARTS (Velas + Heatmap LiqScope) -->
            <div id="tv-chart-container" class="w-full flex flex-col gap-2 py-1">
              <!-- TV Control Bar & Interactive HUD -->
              <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 px-1">
                <!-- Timeframe Selector -->
                <div class="flex items-center gap-1">
                  <span class="text-[10px] font-mono text-outline uppercase mr-1">Temporalidad:</span>
                  <div class="inline-flex rounded-lg border border-surface-border p-0.5 bg-surface gap-0.5">
                    <button id="tf-15m" onclick="changeTvTimeframe('15m')" class="px-2 py-0.5 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer">15m</button>
                    <button id="tf-1h" onclick="changeTvTimeframe('1h')" class="px-2 py-0.5 rounded text-[11px] font-mono font-bold text-mark bg-surface-card border border-mark/30 transition-all cursor-pointer shadow-xs">1h</button>
                    <button id="tf-4h" onclick="changeTvTimeframe('4h')" class="px-2 py-0.5 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer">4h</button>
                    <button id="tf-1d" onclick="changeTvTimeframe('1d')" class="px-2 py-0.5 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer">1D</button>
                  </div>
                </div>

                <!-- LiqScope Palette, Horizon & Intensity Controls & Overlays Toggle -->
                <div class="flex items-center gap-2 flex-wrap">
                  <!-- Horizon Selector -->
                  <div class="flex items-center gap-1">
                    <span class="text-[10px] font-mono text-outline uppercase hidden sm:inline">Horizonte:</span>
                    <select id="tv-horizon-select" onchange="changeTimeframeHorizon(this.value)" class="px-2 py-1 rounded-lg text-[11px] font-mono font-bold text-mark bg-surface border border-surface-border cursor-pointer focus:outline-none focus:border-mark" title="Horizonte temporal de acumulación de posiciones LiqScope">
                      <option value="12h">⏱️ 12h</option>
                      <option value="24h" selected>⏱️ 24h</option>
                      <option value="3d">⏱️ 3d</option>
                      <option value="1w">⏱️ 1w</option>
                      <option value="1m">⏱️ 1m</option>
                      <option value="3m">⏱️ 3m</option>
                    </select>
                  </div>

                  <!-- Palette Selector -->
                  <div class="flex items-center gap-1">
                    <span class="text-[10px] font-mono text-outline uppercase hidden sm:inline">Paleta:</span>
                    <select id="tv-palette-select" onchange="changeTvPalette(this.value)" class="px-2 py-1 rounded-lg text-[11px] font-mono font-bold text-white bg-surface border border-surface-border cursor-pointer focus:outline-none focus:border-mark">
                      <option value="liqscope" selected>🔥 LiqScope Turbo</option>
                      <option value="longshort">🟢🔴 Longs / Shorts</option>
                      <option value="plasma">⚡ Plasma Neón</option>
                    </select>
                  </div>

                  <!-- Intensity Selector -->
                  <div class="flex items-center gap-1">
                    <span class="text-[10px] font-mono text-outline uppercase hidden sm:inline">Brillo:</span>
                    <select id="tv-intensity-select" onchange="changeTvIntensity(this.value)" class="px-2 py-1 rounded-lg text-[11px] font-mono font-bold text-white bg-surface border border-surface-border cursor-pointer focus:outline-none focus:border-mark">
                      <option value="1.0">1.0x Normal</option>
                      <option value="1.5" selected>1.5x Brillante</option>
                      <option value="2.0">2.0x Intenso</option>
                      <option value="2.8">2.8x Rayos X</option>
                    </select>
                  </div>

                  <!-- Auto-Fit Zoom -->
                  <button onclick="resetTvChartZoom()" class="px-2 py-1 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer" title="Auto-ajustar zoom y escala">
                    <span class="material-symbols-outlined text-[13px]">restart_alt</span>
                    <span class="hidden sm:inline">Auto</span>
                  </button>

                  <!-- Súper Gráficos Sub-panels (OI & Funding) -->
                  <button id="btn-toggle-sub-oi" onclick="toggleTvSubChart('oi')" class="px-2.5 py-1 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer" title="Activar/Desactivar sub-panel sincronizado de Open Interest">
                    <span class="material-symbols-outlined text-[13px] text-cyan-400">query_stats</span>
                    <span class="hidden md:inline">Sub-panel</span> <span>OI</span>
                  </button>

                  <button id="btn-toggle-sub-funding" onclick="toggleTvSubChart('funding')" class="px-2.5 py-1 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer" title="Activar/Desactivar sub-panel sincronizado de Funding Histórico">
                    <span class="material-symbols-outlined text-[13px] text-amber-400">hourglass_bottom</span>
                    <span class="hidden md:inline">Sub-panel</span> <span>Funding</span>
                  </button>

                  <!-- Heatmap Toggle -->
                  <button id="btn-toggle-tv-overlays" onclick="toggleTvLiquidationOverlays()" class="px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-mark bg-mark/10 border border-mark/25 flex items-center gap-1 transition-all cursor-pointer" title="Activar/Desactivar mapa de calor LiqScope">
                    <span class="material-symbols-outlined text-[14px]">local_fire_department</span>
                    <span id="tv-overlay-text">Heatmap: ON</span>
                  </button>
                </div>
              </div>

              <!-- Interactive Candle HUD -->
              <div id="tv-hud-bar" class="w-full px-3 py-1.5 rounded-lg bg-surface-card/70 border border-surface-border flex items-center justify-between text-[11px] font-mono text-outline flex-wrap gap-2">
                <div class="flex items-center gap-3">
                  <span id="hud-symbol" class="text-white font-bold">BTCUSDT 1H</span>
                  <span>O: <strong id="hud-open" class="text-white">--</strong></span>
                  <span>H: <strong id="hud-high" class="text-white">--</strong></span>
                  <span>L: <strong id="hud-low" class="text-white">--</strong></span>
                  <span>C: <strong id="hud-close" class="text-white">--</strong></span>
                </div>
                <div class="flex items-center gap-3">
                  <span>Vol: <strong id="hud-vol" class="text-white">--</strong></span>
                  <span id="hud-funding-rate" class="text-cyan-400 font-semibold hidden md:inline">Funding: --</span>
                  <span id="hud-active-wall" class="text-mark font-semibold hidden sm:inline">Heatmap LiqScope: Activo</span>
                </div>
              </div>

              <!-- Canvas Container for TradingView & LiqScope Heatmap -->
              <div id="tv-chart-canvas" class="w-full h-[480px] sm:h-[540px] rounded-xl overflow-hidden bg-[#07090e] border border-surface-border relative shadow-inner select-none">
                <!-- Layer 0: LiqScope Heatmap Background Canvas Underlay -->
                <canvas id="tv-heatmap-canvas" class="absolute inset-0 pointer-events-none z-0"></canvas>

                <!-- Layer 1: TradingView Lightweight Charts (Transparent Candles) -->
                <div id="tv-lw-container" class="absolute inset-0 z-10"></div>

                <!-- Layer 2: LiqScope Heat Legend Overlay -->
                <div id="tv-liqscope-legend" class="absolute bottom-5 left-3 z-20 pointer-events-none flex items-center gap-2 px-2.5 py-1 rounded bg-[#07090e]/90 backdrop-blur border border-surface-border text-[10px] font-mono text-outline shadow-md">
                  <span class="font-bold text-white uppercase tracking-wider text-[9px] flex items-center gap-1">
                    <span class="w-1.5 h-1.5 rounded-full bg-mark animate-pulse"></span>
                    LiqScope Heat:
                  </span>
                  <span class="text-indigo-400 font-semibold">Bajo</span>
                  <div id="tv-legend-gradient-bar" class="w-24 h-2 rounded bg-gradient-to-r from-[#181f5c] via-[#00bfff] via-[#50f05a] to-[#ffff00]"></div>
                  <span class="text-yellow-400 font-bold">Ultra Alto</span>
                </div>
              </div>

              <!-- SÚPER GRÁFICOS: SUB-PANEL 1 OPEN INTEREST (USD) -->
              <div id="tv-subchart-oi-container" class="hidden w-full h-[130px] rounded-xl overflow-hidden bg-[#07090e] border border-surface-border relative shadow-inner mt-2">
                <div class="absolute top-2 left-3 z-20 pointer-events-none flex items-center gap-2 text-[10px] font-mono bg-[#07090e]/90 backdrop-blur px-2.5 py-0.5 rounded border border-surface-border/60">
                  <span class="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
                  <span class="text-cyan-400 font-bold uppercase tracking-wider">Open Interest USD:</span>
                  <span id="sub-oi-hud-val" class="text-white font-bold">--</span>
                </div>
                <div id="tv-sub-oi-lw" class="w-full h-full"></div>
              </div>

              <!-- SÚPER GRÁFICOS: SUB-PANEL 2 FUNDING RATE HISTÓRICO (8H) -->
              <div id="tv-subchart-funding-container" class="hidden w-full h-[115px] rounded-xl overflow-hidden bg-[#07090e] border border-surface-border relative shadow-inner mt-2">
                <div class="absolute top-2 left-3 z-20 pointer-events-none flex items-center gap-2 text-[10px] font-mono bg-[#07090e]/90 backdrop-blur px-2.5 py-0.5 rounded border border-surface-border/60">
                  <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
                  <span class="text-amber-400 font-bold uppercase tracking-wider">Histórico Funding (8h):</span>
                  <span id="sub-funding-hud-val" class="text-white font-bold">--</span>
                </div>
                <div id="tv-sub-funding-lw" class="w-full h-full"></div>
              </div>
            </div>

            <!-- VIEW 2: VISUAL LIQUIDATION DEPTH PROFILE (Interactive Graphic) -->
            <div id="depth-chart-container" class="hidden w-full flex flex-col gap-2 py-1">
              <div class="flex items-center justify-between text-[10px] font-mono text-outline px-1">
                <span>← Niveles Superiores (Short Walls)</span>
                <span class="text-mark font-bold">Láser Mark Price</span>
                <span>Niveles Inferiores (Long Supports) →</span>
              </div>
              <div id="chart-svg-wrapper" class="w-full bg-surface rounded-xl p-2 sm:p-3 border border-surface-border-subtle relative overflow-hidden min-h-[380px] max-h-[580px] overflow-y-auto custom-scroll">
                <!-- SVG Profile Rendered Dynamically -->
              </div>
            </div>

            <!-- VIEW 3: DOM LADDER MATRIX (Tabular Clean List) -->
            <div id="ladder-view-wrapper" class="hidden flex-col gap-1.5">
              <div id="ladder-container" class="space-y-1.5 max-h-[540px] overflow-y-auto custom-scroll pr-1">
                <!-- Rendered dynamically -->
              </div>
            </div>

            <!-- Heat Scale Legend -->
            <div class="flex flex-col sm:flex-row items-center justify-between pt-2 border-t border-surface-border gap-2 text-[11px] font-mono text-outline">
              <div class="flex items-center gap-2">
                <span>Densidad:</span>
                <span class="text-outline">Baja</span>
                <div class="w-24 sm:w-32 h-1.5 rounded-full bg-gradient-to-r from-surface-border via-magnet to-long"></div>
                <span class="text-long font-bold">Ultra Alta ($500M+)</span>
              </div>
              <span class="text-[10px] text-outline">Clic en cualquier fila para inspección</span>
            </div>

          </div>

        </div>

      </div>

    </div>

    <!-- TAB: REKT TICKER (REAL-TIME LIVE LIQUIDATIONS STREAM) -->
    <div id="tab-rekt-ticker" class="tab-pane hidden flex flex-col space-y-4">

      <!-- Header & WebSocket Control Bar -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-xl flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-short/15 border border-short/30 flex items-center justify-center text-short shrink-0">
            <span class="material-symbols-outlined text-[24px] animate-pulse">flash_on</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base sm:text-lg font-mono font-black text-white tracking-tight">REKT Ticker en Directo</h2>
              <span id="rekt-ws-badge" class="px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold border border-emerald-500/30 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                <span id="rekt-ws-status-text">WS CONECTADO</span>
              </span>
            </div>
            <p class="text-xs text-outline font-mono">Flujo en tiempo real de liquidaciones forzadas ejecutadas en Binance Futures.</p>
          </div>
        </div>

        <!-- Controls: Sound + Thresholds + Clean -->
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Audio Toggle Button -->
          <button id="rekt-audio-toggle" onclick="toggleRektAudio()" class="px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-white hover:border-mark font-mono text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer">
            <span class="material-symbols-outlined text-[16px] text-mark" id="rekt-audio-icon">volume_up</span>
            <span id="rekt-audio-text">Audio: ON</span>
          </button>

          <!-- Audio Trigger Threshold Selector -->
          <select id="rekt-audio-threshold" onchange="setRektAudioThreshold(this.value)" class="px-2.5 py-1.5 rounded-lg bg-surface border border-surface-border text-white text-xs font-mono font-semibold focus:outline-none focus:border-mark cursor-pointer" title="Umbral de sonido">
            <option value="0">Sonido: Todas</option>
            <option value="25000">Sonido: > $25K</option>
            <option value="100000" selected>Sonido: > $100K 🐳</option>
            <option value="500000">Sonido: > $500K 🐋</option>
          </select>

          <!-- Test Audio Button -->
          <button onclick="playRektAudio(150000, 'LONG')" class="px-2.5 py-1.5 rounded-lg bg-surface hover:bg-surface-card border border-surface-border text-outline hover:text-white font-mono text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer" title="Probar sonido">
            <span class="material-symbols-outlined text-[15px]">play_circle</span>
            <span>Test 🐳</span>
          </button>

          <!-- Clear Table -->
          <button onclick="clearRektTable()" class="px-2.5 py-1.5 rounded-lg bg-surface hover:bg-surface-card border border-surface-border text-outline hover:text-white font-mono text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer" title="Limpiar lista">
            <span class="material-symbols-outlined text-[15px]">delete_sweep</span>
            <span>Limpiar</span>
          </button>
        </div>
      </div>

      <!-- Live Session KPIs (4 Cards) -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- 1. Total Session Volume -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-md flex flex-col justify-between">
          <div class="flex items-center justify-between text-outline text-[11px] font-mono">
            <span>Total Liquidado (Sesión)</span>
            <span class="material-symbols-outlined text-[16px] text-mark">monitoring</span>
          </div>
          <div class="mt-2 flex flex-col">
            <span id="rekt-stat-total-usd" class="font-mono text-xl sm:text-2xl font-black text-white">$0.00</span>
            <span id="rekt-stat-total-count" class="font-mono text-[11px] text-outline">0 liquidaciones</span>
          </div>
        </div>

        <!-- 2. Longs Liquidated (Downtrend Squeeze) -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-md flex flex-col justify-between">
          <div class="flex items-center justify-between text-outline text-[11px] font-mono">
            <span>Longs Liquidados (Caídas)</span>
            <span class="material-symbols-outlined text-[16px] text-short">trending_down</span>
          </div>
          <div class="mt-2 flex flex-col">
            <span id="rekt-stat-long-usd" class="font-mono text-xl sm:text-2xl font-black text-short">$0.00</span>
            <span id="rekt-stat-long-ratio" class="font-mono text-[11px] text-outline">0 órdenes (0.0%)</span>
          </div>
        </div>

        <!-- 3. Shorts Liquidated (Short Squeezes) -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-md flex flex-col justify-between">
          <div class="flex items-center justify-between text-outline text-[11px] font-mono">
            <span>Shorts Liquidados (Subidas)</span>
            <span class="material-symbols-outlined text-[16px] text-long">trending_up</span>
          </div>
          <div class="mt-2 flex flex-col">
            <span id="rekt-stat-short-usd" class="font-mono text-xl sm:text-2xl font-black text-long">$0.00</span>
            <span id="rekt-stat-short-ratio" class="font-mono text-[11px] text-outline">0 órdenes (0.0%)</span>
          </div>
        </div>

        <!-- 4. Whale Liquidations -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-md flex flex-col justify-between">
          <div class="flex items-center justify-between text-outline text-[11px] font-mono">
            <span>Ballenas (> $100K)</span>
            <span class="material-symbols-outlined text-[16px] text-amber-400">workspace_premium</span>
          </div>
          <div class="mt-2 flex flex-col">
            <span id="rekt-stat-whale-count" class="font-mono text-xl sm:text-2xl font-black text-amber-400">0</span>
            <span id="rekt-stat-largest" class="font-mono text-[11px] text-outline truncate">Mayor: --</span>
          </div>
        </div>
      </div>

      <!-- Feed Table Section with Live Filter Controls -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-xl flex flex-col space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2 border-b border-surface-border-subtle">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-mark text-[18px]">stream</span>
            <span class="font-mono text-xs font-bold text-white uppercase tracking-wider">Flujo de Órdenes Forzadas en Tiempo Real</span>
            <span id="rekt-count-badge" class="px-2 py-0.5 rounded bg-surface font-mono text-[10px] text-outline">0 eventos</span>
          </div>

          <!-- Symbol & Size Filters -->
          <div class="flex items-center gap-2 flex-wrap">
            <select id="rekt-filter-symbol" onchange="filterRektFeed()" class="px-2.5 py-1 text-xs font-mono font-semibold rounded bg-surface border border-surface-border text-white focus:outline-none focus:border-mark cursor-pointer">
              <option value="ALL">Todos los pares</option>
              <option value="BTCUSDT">Solo BTC/USDT</option>
              <option value="ETHUSDT">Solo ETH/USDT</option>
              <option value="ALTS">Solo Altcoins</option>
            </select>

            <select id="rekt-filter-min-size" onchange="filterRektFeed()" class="px-2.5 py-1 text-xs font-mono font-semibold rounded bg-surface border border-surface-border text-white focus:outline-none focus:border-mark cursor-pointer">
              <option value="0">Cualquier importe</option>
              <option value="10000">> $10,000</option>
              <option value="50000">> $50,000</option>
              <option value="100000">> $100,000 🐳</option>
              <option value="500000">> $500,000 🐋</option>
            </select>
          </div>
        </div>

        <!-- Table Container -->
        <div class="overflow-x-auto max-h-[560px] overflow-y-auto">
          <table class="w-full text-left font-mono text-xs">
            <thead class="sticky top-0 bg-surface-card border-b border-surface-border text-[11px] text-outline uppercase tracking-wider">
              <tr>
                <th class="py-2.5 px-3">Hora</th>
                <th class="py-2.5 px-3">Par</th>
                <th class="py-2.5 px-3">Liquidación</th>
                <th class="py-2.5 px-3 text-right">Precio Ejecutado</th>
                <th class="py-2.5 px-3 text-right">Cantidad</th>
                <th class="py-2.5 px-3 text-right">Volumen Nocional</th>
                <th class="py-2.5 px-3 text-center">Clasificación</th>
              </tr>
            </thead>
            <tbody id="rekt-table-body" class="divide-y divide-surface-border/40">
              <tr id="rekt-empty-row">
                <td colspan="7" class="py-8 text-center text-outline font-mono text-xs">
                  <div class="flex flex-col items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[32px] text-outline animate-spin">sync</span>
                    <span>Conectando al stream en tiempo real y esperando liquidaciones...</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB: TASAS DE FINANCIACIÓN (FUNDING RATES MATRIX) -->
    <div id="tab-financiacion" class="tab-pane hidden flex flex-col space-y-4">
      <!-- Funding Header Banner with Live Clock -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-cyan-500/15 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shrink-0 shadow-xs">
            <span class="material-symbols-outlined text-[24px]">percent</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-base sm:text-lg font-bold text-white font-mono flex items-center gap-2">
                <span>Tasas de Financiación (Funding Rates Matrix)</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">BINANCE + BYBIT</span>
              </h2>
            </div>
            <p class="text-xs text-outline font-mono mt-0.5">
              Supervisión de tasas de interés periódico cada 8 horas. Detecta recalentamiento en posiciones alcistas o bajistas.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2 self-stretch sm:self-auto justify-between sm:justify-end">
          <div class="px-3 py-1.5 rounded-lg bg-surface border border-surface-border flex items-center gap-2 font-mono text-xs">
            <span class="material-symbols-outlined text-cyan-400 text-[16px] animate-pulse">timer</span>
            <span class="text-outline text-[11px]">Próximo Cobro:</span>
            <span id="funding-countdown-clock" class="text-cyan-300 font-bold tracking-wider">--:--:--</span>
          </div>
          <button onclick="fetchFundingRates()" class="px-2.5 py-1.5 rounded-lg bg-surface border border-surface-border text-outline hover:text-white transition-all cursor-pointer flex items-center gap-1" title="Actualizar tasas ahora">
            <span class="material-symbols-outlined text-[16px]">sync</span>
          </button>
        </div>
      </div>

      <!-- Top 3 Hero KPI Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <!-- BTC Funding Card -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-sm flex flex-col space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-amber-400/20 text-amber-400 flex items-center justify-center text-xs font-bold font-mono">₿</span>
              <span class="font-mono text-sm font-bold text-white">BTCUSDT</span>
            </div>
            <span id="card-btc-bias-pill" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-surface border border-surface-border text-cyan-300">Longs pagan</span>
          </div>
          <div class="flex items-baseline justify-between pt-1">
            <div class="flex flex-col">
              <span class="text-[10px] font-mono text-outline uppercase">Tasa Media (8h)</span>
              <span id="card-btc-avg-rate" class="text-lg font-mono font-black text-cyan-400">+0.0100%</span>
            </div>
            <div class="flex flex-col items-end">
              <span class="text-[10px] font-mono text-outline uppercase">Anualizado APR</span>
              <span id="card-btc-apr" class="text-sm font-mono font-bold text-white">+10.95%</span>
            </div>
          </div>
          <div class="pt-2 border-t border-surface-border-subtle flex items-center justify-between text-[11px] font-mono text-outline">
            <span>Binance: <strong id="card-btc-binance" class="text-white">--</strong></span>
            <span>Bybit: <strong id="card-btc-bybit" class="text-white">--</strong></span>
          </div>
        </div>

        <!-- ETH Funding Card -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-sm flex flex-col space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <span class="w-6 h-6 rounded-full bg-indigo-400/20 text-indigo-400 flex items-center justify-center text-xs font-bold font-mono">Ξ</span>
              <span class="font-mono text-sm font-bold text-white">ETHUSDT</span>
            </div>
            <span id="card-eth-bias-pill" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-surface border border-surface-border text-cyan-300">Longs pagan</span>
          </div>
          <div class="flex items-baseline justify-between pt-1">
            <div class="flex flex-col">
              <span class="text-[10px] font-mono text-outline uppercase">Tasa Media (8h)</span>
              <span id="card-eth-avg-rate" class="text-lg font-mono font-black text-cyan-400">+0.0100%</span>
            </div>
            <div class="flex flex-col items-end">
              <span class="text-[10px] font-mono text-outline uppercase">Anualizado APR</span>
              <span id="card-eth-apr" class="text-sm font-mono font-bold text-white">+10.95%</span>
            </div>
          </div>
          <div class="pt-2 border-t border-surface-border-subtle flex items-center justify-between text-[11px] font-mono text-outline">
            <span>Binance: <strong id="card-eth-binance" class="text-white">--</strong></span>
            <span>Bybit: <strong id="card-eth-bybit" class="text-white">--</strong></span>
          </div>
        </div>

        <!-- Sentiment Thermometer Card -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 shadow-sm flex flex-col space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-mono text-xs font-bold text-outline uppercase tracking-wider flex items-center gap-1.5">
              <span class="material-symbols-outlined text-[16px] text-mark">thermostat</span>
              <span>Barómetro Térmico Global</span>
            </span>
            <span id="global-overheated-badge" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-surface border border-surface-border text-outline">0 Pares en Alerta</span>
          </div>
          <div class="flex flex-col pt-1">
            <span class="text-[10px] font-mono text-outline uppercase">Sesgo Dominante</span>
            <span id="global-market-bias" class="text-sm font-mono font-bold text-mark truncate">MODERADAMENTE ALCISTA</span>
          </div>
          <div class="pt-2 border-t border-surface-border-subtle flex items-center justify-between text-[11px] font-mono text-outline">
            <span>Media Global de Mercado:</span>
            <strong id="global-avg-funding" class="text-white font-bold">+0.0085%</strong>
          </div>
        </div>
      </div>

      <!-- Funding Matrix Table Card -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md flex flex-col space-y-3">
        <!-- Table Toolbar: Search & Quick Filter Pills -->
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-surface-border">
          <div class="flex items-center gap-2 flex-wrap">
            <div class="relative">
              <span class="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-outline text-[16px]">search</span>
              <input type="text" id="funding-search-input" oninput="filterFundingTable()" placeholder="Buscar por símbolo (ej. SOL, DOGE)..." class="pl-8 pr-3 py-1.5 rounded-lg bg-surface border border-surface-border text-white text-xs font-mono placeholder-slate-500 w-56 sm:w-64 focus:outline-none focus:border-cyan-400">
            </div>
            
            <div class="inline-flex rounded-lg border border-surface-border p-0.5 bg-surface gap-0.5">
              <button onclick="setFundingFilter('all')" id="btn-ff-all" class="px-2.5 py-1 rounded text-[11px] font-mono font-bold text-cyan-300 bg-surface-card border border-cyan-500/30 transition-all cursor-pointer">Todos</button>
              <button onclick="setFundingFilter('overheated')" id="btn-ff-overheated" class="px-2.5 py-1 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer">🔥 Sobrecalentados</button>
              <button onclick="setFundingFilter('longs_pay')" id="btn-ff-longs_pay" class="px-2.5 py-1 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer">🟢 Longs pagan</button>
              <button onclick="setFundingFilter('shorts_pay')" id="btn-ff-shorts_pay" class="px-2.5 py-1 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer">🔴 Shorts pagan</button>
            </div>
          </div>

          <div class="text-[11px] font-mono text-outline flex items-center gap-2">
            <span>Mostrando: <strong id="funding-count-display" class="text-white">--</strong> pares</span>
          </div>
        </div>

        <!-- Table Responsive Container -->
        <div class="overflow-x-auto rounded-lg border border-surface-border-subtle custom-scroll max-h-[580px]">
          <table class="w-full text-left font-mono text-xs border-collapse">
            <thead class="sticky top-0 bg-[#07090e] border-b border-surface-border text-[10px] text-outline uppercase tracking-wider z-10">
              <tr>
                <th class="py-2.5 px-3">Par / Activo</th>
                <th class="py-2.5 px-3">Precio Mark</th>
                <th class="py-2.5 px-3">Tasa Binance (8h)</th>
                <th class="py-2.5 px-3">Tasa Bybit (8h)</th>
                <th class="py-2.5 px-3">Media (8h)</th>
                <th class="py-2.5 px-3">APR Anual</th>
                <th class="py-2.5 px-3">Flujo de Comisiones</th>
                <th class="py-2.5 px-3 text-right">Semáforo Térmico</th>
              </tr>
            </thead>
            <tbody id="funding-table-body" class="divide-y divide-surface-border/40 bg-surface/30">
              <tr>
                <td colspan="8" class="py-8 text-center text-outline font-mono text-xs">
                  <div class="flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[20px] animate-spin text-cyan-400">sync</span>
                    <span>Cargando matriz de tasas de financiación multi-exchange...</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB: SCREENER DE GANADORAS, PERDEDORAS Y OI SURGE (BALLENAS) -->
    <div id="tab-screener" class="tab-pane hidden flex flex-col space-y-4">
      <!-- Screener Header Banner with Market Breadth Barometer -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-yellow-500/15 border border-yellow-500/30 flex items-center justify-center text-yellow-400 shrink-0 shadow-xs">
            <span class="material-symbols-outlined text-[24px]">military_tech</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-mono text-[10px] uppercase tracking-widest text-yellow-400 font-bold">LiqScope Market Screener</span>
              <span class="px-2 py-0.5 rounded-full bg-yellow-400/10 text-yellow-300 font-mono text-[10px] font-bold border border-yellow-400/20 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-yellow-400 animate-pulse"></span>
                Radar Ballenas Activo
              </span>
            </div>
            <h2 class="text-lg font-bold text-white tracking-tight">Ganadoras, Perdedoras & Acumulación Institucional</h2>
          </div>
        </div>

        <!-- Market Breadth Barometer -->
        <div class="w-full lg:w-auto flex flex-col sm:flex-row items-stretch sm:items-center gap-3 bg-surface/60 border border-surface-border p-3 rounded-xl">
          <div class="flex flex-col gap-1 min-w-[240px]">
            <div class="flex items-center justify-between text-[11px] font-mono">
              <span class="text-long font-bold flex items-center gap-1"><span class="w-2 h-2 rounded-full bg-long"></span> Alcistas: <strong id="screener-adv-pct">--%</strong></span>
              <span class="text-short font-bold flex items-center gap-1">Bajistas: <strong id="screener-dec-pct">--%</strong> <span class="w-2 h-2 rounded-full bg-short"></span></span>
            </div>
            <div class="w-full h-2 rounded-full bg-surface-border overflow-hidden flex">
              <div id="screener-bar-adv" class="h-full bg-long transition-all duration-500" style="width: 50%"></div>
              <div id="screener-bar-dec" class="h-full bg-short transition-all duration-500" style="width: 50%"></div>
            </div>
          </div>
          <div class="h-7 w-px bg-surface-border hidden sm:block"></div>
          <div class="flex items-center gap-3 text-xs font-mono">
            <div>
              <span class="text-outline text-[10px] block">OI Global:</span>
              <span id="screener-global-oi" class="text-cyan-400 font-bold">--</span>
            </div>
            <div>
              <span class="text-outline text-[10px] block">Volumen 24h:</span>
              <span id="screener-global-vol" class="text-white font-bold">--</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Top 3 Hero Cards (Top Gainer, Top Loser, Whale Surge) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <!-- Card 1: Top Gainer -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 flex items-center justify-between shadow-xs hover:border-long/40 transition-all cursor-pointer" onclick="filterScreenerTab('gainers')">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-long/15 border border-long/30 flex items-center justify-center text-long font-bold font-mono text-base">
              🚀
            </div>
            <div>
              <span class="text-[10px] font-mono text-outline uppercase font-semibold block">Top Gainer 24h</span>
              <div class="flex items-center gap-1.5">
                <span id="hero-gainer-sym" class="text-white font-bold font-mono text-sm">--</span>
                <span id="hero-gainer-pct" class="text-long font-bold font-mono text-xs">+0.0%</span>
              </div>
            </div>
          </div>
          <div class="text-right font-mono">
            <span id="hero-gainer-price" class="text-white font-bold text-xs block">--</span>
            <span id="hero-gainer-oi" class="text-[10px] text-cyan-400">OI: --</span>
          </div>
        </div>

        <!-- Card 2: Top Loser -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 flex items-center justify-between shadow-xs hover:border-short/40 transition-all cursor-pointer" onclick="filterScreenerTab('losers')">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-short/15 border border-short/30 flex items-center justify-center text-short font-bold font-mono text-base">
              🔻
            </div>
            <div>
              <span class="text-[10px] font-mono text-outline uppercase font-semibold block">Top Loser 24h</span>
              <div class="flex items-center gap-1.5">
                <span id="hero-loser-sym" class="text-white font-bold font-mono text-sm">--</span>
                <span id="hero-loser-pct" class="text-short font-bold font-mono text-xs">-0.0%</span>
              </div>
            </div>
          </div>
          <div class="text-right font-mono">
            <span id="hero-loser-price" class="text-white font-bold text-xs block">--</span>
            <span id="hero-loser-oi" class="text-[10px] text-cyan-400">OI: --</span>
          </div>
        </div>

        <!-- Card 3: Whale Surge -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-3.5 flex items-center justify-between shadow-xs hover:border-yellow-400/40 transition-all cursor-pointer" onclick="filterScreenerTab('oi_surge')">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-yellow-400/15 border border-yellow-400/30 flex items-center justify-center text-yellow-400 font-bold font-mono text-base">
              🐋
            </div>
            <div>
              <span class="text-[10px] font-mono text-outline uppercase font-semibold block">Pico de Ballenas (OI)</span>
              <div class="flex items-center gap-1.5">
                <span id="hero-whale-sym" class="text-white font-bold font-mono text-sm">--</span>
                <span id="hero-whale-spike" class="text-yellow-400 font-bold font-mono text-xs">+0.0%</span>
              </div>
            </div>
          </div>
          <div class="text-right font-mono">
            <span id="hero-whale-sig" class="px-1.5 py-0.5 rounded bg-yellow-400/15 text-yellow-300 font-bold text-[9px] block">ACUMULACIÓN</span>
            <span id="hero-whale-vol" class="text-[10px] text-outline">Vol: --</span>
          </div>
        </div>
      </div>

      <!-- Quick Category Filters, Search Bar & Table -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md space-y-3.5">
        <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
          <!-- Category Tabs -->
          <div class="flex items-center gap-1.5 overflow-x-auto custom-scroll pb-1 sm:pb-0">
            <button onclick="filterScreenerTab('all')" id="sc-filter-all" class="px-3 py-1.5 rounded-lg text-xs font-mono font-bold text-mark bg-surface-card border border-mark/30 transition-all cursor-pointer">
              🌐 Todos los Pares
            </button>
            <button onclick="filterScreenerTab('gainers')" id="sc-filter-gainers" class="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer">
              <span>🔥 Top Gainers</span>
            </button>
            <button onclick="filterScreenerTab('losers')" id="sc-filter-losers" class="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer">
              <span>🔻 Top Losers</span>
            </button>
            <button onclick="filterScreenerTab('oi_surge')" id="sc-filter-oi_surge" class="px-3 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer">
              <span>🐋 Radar Ballenas</span>
            </button>
          </div>

          <!-- Search Input -->
          <div class="relative w-full sm:w-64">
            <span class="material-symbols-outlined absolute left-2.5 top-1/2 -translate-y-1/2 text-outline text-[16px]">search</span>
            <input type="text" id="screener-search-input" oninput="handleScreenerSearch(this.value)" placeholder="Buscar par (BTC, SOL, DOGE)..." class="w-full bg-surface border border-surface-border rounded-lg pl-8 pr-3 py-1.5 text-xs font-mono text-white placeholder-outline focus:outline-none focus:border-mark">
          </div>
        </div>

        <!-- Screener Table -->
        <div class="w-full overflow-x-auto rounded-lg border border-surface-border/60">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="border-b border-surface-border/80 bg-surface/80 text-outline font-mono text-[10px] uppercase tracking-wider">
                <th class="py-2.5 px-3">#</th>
                <th class="py-2.5 px-3">Par / Moneda</th>
                <th class="py-2.5 px-3">Precio Actual</th>
                <th class="py-2.5 px-3">Cambio 24h</th>
                <th class="py-2.5 px-3">Rango 24h (Min - Max)</th>
                <th class="py-2.5 px-3">Open Interest (USD)</th>
                <th class="py-2.5 px-3">Delta OI / Ballena</th>
                <th class="py-2.5 px-3">Volumen 24h</th>
                <th class="py-2.5 px-3">Funding (8h)</th>
                <th class="py-2.5 px-3 text-right">Acción</th>
              </tr>
            </thead>
            <tbody id="screener-table-body" class="divide-y divide-surface-border/40 bg-surface/30">
              <tr>
                <td colspan="10" class="py-8 text-center text-outline font-mono text-xs">
                  <div class="flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[20px] animate-spin text-yellow-400">sync</span>
                    <span>Cargando screener de derivados y radar de ballenas...</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB: TRACKER INSTITUCIONAL DE ETFS SPOT (BITCOIN & ETHEREUM) -->
    <div id="tab-etfs" class="tab-pane hidden flex flex-col space-y-4">
      <!-- ETF Header Banner with Asset Switcher -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0 shadow-xs">
            <span class="material-symbols-outlined text-[24px]">account_balance</span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-mono text-[10px] uppercase tracking-widest text-emerald-400 font-bold">LiqScope Institucional</span>
              <span id="etf-sentiment-badge" class="px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-300 font-mono text-[10px] font-bold border border-emerald-400/20 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                Inflow Institucional Positivo
              </span>
            </div>
            <h2 class="text-lg font-bold text-white tracking-tight">Tracker de ETFs Spot (Bitcoin & Ethereum)</h2>
          </div>
        </div>

        <!-- Asset Toggle Buttons (BTC vs ETH) -->
        <div class="inline-flex rounded-xl border border-surface-border p-1 bg-surface gap-1">
          <button id="etf-btn-btc" onclick="switchEtfAsset('BTC')" class="px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold text-mark bg-surface-card border border-mark/30 transition-all cursor-pointer shadow-xs flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-mark"></span>
            <span>₿ Bitcoin ETFs</span>
          </button>
          <button id="etf-btn-eth" onclick="switchEtfAsset('ETH')" class="px-3.5 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-cyan-400"></span>
            <span>Ξ Ethereum ETFs</span>
          </button>
        </div>
      </div>

      <!-- 4 Hero Metric Cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        <!-- Card 1: Flujo Neto Diario -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-4 space-y-1 shadow-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono text-outline uppercase font-semibold">Flujo Neto Última Sesión</span>
            <span class="material-symbols-outlined text-[16px] text-emerald-400">trending_up</span>
          </div>
          <span id="etf-metric-today-inflow" class="text-xl font-bold font-mono text-long block">+$285.4M</span>
          <span id="etf-metric-today-coins" class="text-[11px] font-mono text-outline block">~3,815 BTC absorbidos</span>
        </div>

        <!-- Card 2: AUM Total Institucional -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-4 space-y-1 shadow-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono text-outline uppercase font-semibold">Activos Totales (AUM)</span>
            <span class="material-symbols-outlined text-[16px] text-cyan-400">shield_lock</span>
          </div>
          <span id="etf-metric-total-aum" class="text-xl font-bold font-mono text-white block">$68.42B USD</span>
          <span id="etf-metric-total-holdings" class="text-[11px] font-mono text-cyan-400 block">1,114,210 BTC en custodia</span>
        </div>

        <!-- Card 3: Inflow Acumulado Histórico -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-4 space-y-1 shadow-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono text-outline uppercase font-semibold">Inflow Histórico Acumulado</span>
            <span class="material-symbols-outlined text-[16px] text-yellow-400">savings</span>
          </div>
          <span id="etf-metric-cum-inflow" class="text-xl font-bold font-mono text-yellow-400 block">+$26.15B USD</span>
          <span class="text-[11px] font-mono text-outline block">Desde aprobación SEC</span>
        </div>

        <!-- Card 4: Fondo Líder -->
        <div class="rounded-xl bg-surface-panel border border-surface-border p-4 space-y-1 shadow-xs">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono text-outline uppercase font-semibold">Fondo Dominante</span>
            <span class="material-symbols-outlined text-[16px] text-mark">trophy</span>
          </div>
          <span id="etf-metric-leader" class="text-base font-bold font-mono text-white block truncate">IBIT (BlackRock)</span>
          <span id="etf-metric-leader-share" class="text-[11px] font-mono text-mark block">49.6% cuota de mercado</span>
        </div>
      </div>

      <!-- Daily Net Inflows Historical Bar Chart -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md space-y-3">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 class="font-bold text-white text-sm flex items-center gap-1.5 font-mono">
              <span class="material-symbols-outlined text-[18px] text-cyan-400">bar_chart</span>
              <span>Histórico de Flujos Netos Diarios ($M USD)</span>
            </h3>
            <span class="text-[11px] font-mono text-outline">Entradas (Verde) vs Salidas / Redenciones (Rojo) en las últimas 14 sesiones</span>
          </div>
          <div class="flex items-center gap-3 text-xs font-mono">
            <span class="flex items-center gap-1 text-long"><span class="w-2.5 h-2.5 rounded-sm bg-long"></span> Inflow Neto</span>
            <span class="flex items-center gap-1 text-short"><span class="w-2.5 h-2.5 rounded-sm bg-short"></span> Outflow Neto</span>
          </div>
        </div>

        <!-- Dynamic Inflow Bars Container -->
        <div id="etf-history-chart-wrapper" class="w-full bg-surface rounded-xl p-3 border border-surface-border-subtle overflow-x-auto custom-scroll">
          <div id="etf-bars-container" class="min-w-[620px] h-[160px] flex items-end justify-between gap-2 pt-4 pb-6 relative">
            <!-- Rendered Dynamically via JS -->
          </div>
        </div>
      </div>

      <!-- Institutional Funds Breakdown Table -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="font-bold text-white text-sm flex items-center gap-1.5 font-mono">
            <span class="material-symbols-outlined text-[18px] text-emerald-400">table_rows</span>
            <span>Desglose Oficial de Fondos Cotizados Registrados ante la SEC</span>
          </h3>
          <span class="text-[10px] font-mono text-outline hidden sm:inline">13F / SEC Institutional Reporting</span>
        </div>

        <div class="w-full overflow-x-auto rounded-lg border border-surface-border/60">
          <table class="w-full text-left border-collapse text-xs font-mono">
            <thead>
              <tr class="border-b border-surface-border/80 bg-surface/80 text-outline text-[10px] uppercase tracking-wider">
                <th class="py-2.5 px-3">Ticker</th>
                <th class="py-2.5 px-3">Emisor / Gestor</th>
                <th class="py-2.5 px-3">Nombre del Fondo</th>
                <th class="py-2.5 px-3">AUM ($ USD)</th>
                <th class="py-2.5 px-3">Holdings en Custodia</th>
                <th class="py-2.5 px-3">Flujo Última Sesión</th>
                <th class="py-2.5 px-3">Inflow Acumulado</th>
                <th class="py-2.5 px-3">Comisión (Fee)</th>
                <th class="py-2.5 px-3 text-right">Custodio</th>
              </tr>
            </thead>
            <tbody id="etf-table-body" class="divide-y divide-surface-border/40 bg-surface/30">
              <tr>
                <td colspan="9" class="py-8 text-center text-outline text-xs">
                  <div class="flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-[20px] animate-spin text-emerald-400">sync</span>
                    <span>Cargando datos institucionales de ETFs Spot...</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <div id="tab-modelo-datos" class="tab-pane hidden flex flex-col space-y-3.5">
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-md flex items-start justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-lg bg-mark/15 border border-mark/30 flex items-center justify-center text-mark shrink-0">
            <span class="material-symbols-outlined text-[20px]">verified_user</span>
          </div>
          <div>
            <span class="font-mono text-[10px] uppercase tracking-widest text-mark font-bold">Protocolo de Integridad</span>
            <h2 class="text-base font-bold text-white">Transparencia Criptográfica de Datos</h2>
          </div>
        </div>
        <span class="px-2 py-0.5 rounded-full bg-surface text-long font-mono text-[10px] flex items-center gap-1 border border-long/20">
          <span class="w-1.5 h-1.5 rounded-full bg-long animate-ping"></span>
          Binance Live Sync
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div class="bg-surface-panel border border-surface-border rounded-xl p-3.5 space-y-2">
          <div class="flex items-start justify-between">
            <div>
              <span class="font-mono text-xs font-bold text-white block">Precio Mark (mark_price)</span>
              <span class="text-[11px] text-on-surface-variant">Binance Futures USDⓈ-M Perps</span>
            </div>
            <span id="model-mark-display" class="font-mono text-base font-bold text-mark">$81,420.50</span>
          </div>
          <div class="bg-surface p-2 rounded flex items-center justify-between gap-2 border border-surface-border-subtle font-mono text-[10px]">
            <span class="text-outline truncate">GET fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT</span>
            <a href="https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT" target="_blank" class="text-mark hover:underline shrink-0">Verificar ↗</a>
          </div>
        </div>

        <div class="bg-surface-panel border border-surface-border rounded-xl p-3.5 space-y-2">
          <div class="flex items-start justify-between">
            <div>
              <span class="font-mono text-xs font-bold text-white block">Interés Abierto Total</span>
              <span class="text-[11px] text-on-surface-variant">total_open_interest_usd</span>
            </div>
            <span id="model-oi-display" class="font-mono text-base font-bold text-magnet">~$7,742M</span>
          </div>
          <div class="bg-surface p-2 rounded flex items-center justify-between gap-2 border border-surface-border-subtle font-mono text-[10px]">
            <span class="text-outline truncate">GET fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT</span>
            <a href="https://fapi.binance.com/fapi/v1/openInterest?symbol=BTCUSDT" target="_blank" class="text-mark hover:underline shrink-0">Verificar ↗</a>
          </div>
        </div>
      </div>

      <!-- Fórmulas -->
      <div class="bg-surface-panel border border-surface-border rounded-xl p-4 space-y-3">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-mark text-[20px]">functions</span>
          <h3 class="text-xs font-bold text-white uppercase tracking-wider">Fórmulas Oficiales de Liquidación Binance</h3>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <div class="bg-surface p-3 rounded-lg border border-long/20 space-y-1">
            <span class="text-long font-bold block">Fórmula Liquidación LONG:</span>
            <code class="text-white block bg-surface-panel p-2 rounded">LiqPrice = EntryPrice × (1 - 1/Lev + MMR)</code>
            <span class="text-outline text-[10px] block">Ej: 50x (MMR 0.5%) → Caída del 1.50% hasta liquidación</span>
          </div>
          <div class="bg-surface p-3 rounded-lg border border-short/20 space-y-1">
            <span class="text-short font-bold block">Fórmula Liquidación SHORT:</span>
            <code class="text-white block bg-surface-panel p-2 rounded">LiqPrice = EntryPrice × (1 + 1/Lev - MMR)</code>
            <span class="text-outline text-[10px] block">Ej: 50x (MMR 0.5%) → Subida del 1.50% hasta liquidación</span>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 3: NIVELES MMR & SIMULADOR COMPLETO -->
    <div id="tab-niveles-mmr" class="tab-pane hidden flex flex-col space-y-3.5">
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 space-y-4 shadow-md">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-base font-bold text-white">Simulador Detallado de Margen de Mantenimiento (MMR)</h2>
            <p class="text-xs text-on-surface-variant">Calcula con precisión el precio de liquidación oficial de Binance Futures USDⓢ-M.</p>
          </div>
        </div>
        <!-- Table -->
        <div class="overflow-x-auto">
          <table class="w-full font-mono text-xs text-left">
            <thead>
              <tr class="border-b border-surface-border text-outline text-[10px]">
                <th class="py-2">Nivel</th>
                <th class="py-2">Valor Nocional (USDT)</th>
                <th class="py-2">Apalancamiento</th>
                <th class="py-2">MMR</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-border-subtle text-slate-300">
              <tr><td class="py-2 text-mark">Tier 1</td><td>0 – 50,000</td><td>100x – 125x</td><td>0.40%</td></tr>
              <tr><td class="py-2 text-mark">Tier 2</td><td>50,000 – 250,000</td><td>50x</td><td>0.50%</td></tr>
              <tr><td class="py-2 text-mark">Tier 3</td><td>250,000 – 1,000,000</td><td>25x</td><td>1.00%</td></tr>
              <tr><td class="py-2 text-mark">Tier 4</td><td>1,000,000 – 5,000,000</td><td>10x</td><td>2.00%</td></tr>
              <tr><td class="py-2 text-mark">Tier 5</td><td>5,000,000+</td><td>5x</td><td>4.00%</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- TAB 4: RADAR DINÁMICO DE ALERTAS & NOTIFICACIONES EN VIVO -->
    <div id="tab-alertas" class="tab-pane hidden flex flex-col space-y-4">

      <!-- Header & Master Controls Card -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-short/15 border border-short/30 flex items-center justify-center text-short shrink-0 shadow-xs relative">
            <span class="material-symbols-outlined text-[22px]">radar</span>
            <span class="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-short animate-ping"></span>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-sm font-mono font-bold text-white tracking-wide">RADAR DE LIQUIDACIONES EN VIVO</h2>
              <span id="radar-live-status" class="px-2 py-0.5 rounded bg-surface-card border border-long/30 text-long font-mono text-[9px] font-bold">RADAR ACTIVO</span>
            </div>
            <p class="text-xs text-on-surface-variant font-mono">Detección reactiva de clústeres inminentes, muros de absorción y asimetría de mercado.</p>
          </div>
        </div>

        <!-- Master Notification & Sound Toggles -->
        <div class="flex items-center gap-2 flex-wrap">
          <!-- Audio Toggle -->
          <button id="btn-toggle-audio" onclick="toggleAudioAlerts()" class="px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-mark/10 border-mark/30 text-white" title="Activar/Desactivar avisos acústicos">
            <span id="audio-icon" class="material-symbols-outlined text-[16px] text-mark">volume_up</span>
            <span id="audio-label">Sonido: ON</span>
          </button>
          
          <!-- Test Sound Ping -->
          <button onclick="playTestPing()" class="px-2.5 py-1.5 rounded-lg border border-surface-border bg-surface-card hover:bg-surface text-outline hover:text-white text-xs font-mono transition-all cursor-pointer flex items-center gap-1" title="Reproducir tono de prueba sonar (Web Audio API)">
            <span class="material-symbols-outlined text-[15px]">play_circle</span>
            <span class="hidden xs:inline">Test Sonar</span>
          </button>

          <!-- Browser Push Notification Button -->
          <button id="btn-toggle-notifs" onclick="toggleBrowserNotifs()" class="px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-surface-card border-surface-border text-on-surface hover:text-white" title="Notificaciones de escritorio o móvil">
            <span id="notif-icon" class="material-symbols-outlined text-[16px] text-magnet">notifications_active</span>
            <span id="notif-label">Push: Activar</span>
          </button>
        </div>
      </div>

      <!-- Telegram Alert Bot Integration Card -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 shadow-xl flex flex-col space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-lg bg-[#2AABEE]/15 border border-[#2AABEE]/30 flex items-center justify-center text-[#2AABEE]">
              <span class="material-symbols-outlined text-[18px]">send</span>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-mono font-bold text-white tracking-wide">TELEGRAM ALERT BOT</span>
                <span id="tg-status-pill" class="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-surface border border-surface-border text-outline">DESCONECTADO</span>
              </div>
              <p class="text-[11px] text-on-surface-variant font-mono">Recibe avisos en tiempo real en tu móvil o canal de Telegram sin mantener la web abierta.</p>
            </div>
          </div>
          <button onclick="toggleTgPanel()" id="btn-tg-toggle-panel" class="text-xs font-mono text-outline hover:text-white flex items-center gap-1 cursor-pointer">
            <span id="tg-panel-toggle-text">Configurar</span>
            <span id="tg-chevron" class="material-symbols-outlined text-[16px]">expand_more</span>
          </button>
        </div>

        <!-- Collapsible Telegram Credentials & Options -->
        <div id="tg-config-body" class="hidden pt-3 border-t border-surface-border flex flex-col space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <!-- Bot Token Input -->
            <div class="flex flex-col gap-1">
              <label class="text-[10px] font-mono text-outline font-semibold uppercase flex items-center justify-between">
                <span>Bot Token (API HTTP)</span>
                <span class="text-[9px] text-[#2AABEE] lowercase">@BotFather</span>
              </label>
              <div class="relative">
                <input id="tg-token-input" type="password" placeholder="Ej: 712345678:AAH..." class="w-full bg-surface border border-surface-border text-white text-xs font-mono rounded-lg px-3 py-2 pr-8 focus:border-[#2AABEE] focus:outline-none placeholder:text-outline/50"/>
                <button type="button" onclick="toggleTokenVisibility()" class="absolute right-2 top-2 text-outline hover:text-white cursor-pointer">
                  <span id="token-vis-icon" class="material-symbols-outlined text-[16px]">visibility</span>
                </button>
              </div>
            </div>

            <!-- Chat ID Input with Auto-detect button -->
            <div class="flex flex-col gap-1">
              <label class="text-[10px] font-mono text-outline font-semibold uppercase flex items-center justify-between">
                <span>Chat ID o Canal</span>
                <button type="button" onclick="autoDetectTelegramChat()" class="text-[9px] text-mark hover:underline cursor-pointer flex items-center gap-0.5" title="Detectar ID a partir de tu mensaje /start">
                  <span class="material-symbols-outlined text-[11px]">sync</span> Detectar mi ID
                </button>
              </label>
              <div class="flex items-center gap-1.5">
                <input id="tg-chat-input" type="text" placeholder="Ej: 123456789 o @tu_canal" class="w-full bg-surface border border-surface-border text-white text-xs font-mono rounded-lg px-3 py-2 focus:border-[#2AABEE] focus:outline-none placeholder:text-outline/50"/>
                <a href="https://t.me/criptobtctrader_bot" target="_blank" rel="noopener" class="px-2.5 py-2 rounded-lg bg-[#2AABEE]/15 hover:bg-[#2AABEE]/25 border border-[#2AABEE]/30 text-[#2AABEE] text-xs font-mono font-bold shrink-0 flex items-center gap-1 cursor-pointer" title="Abrir @criptobtctrader_bot en Telegram">
                  <span class="material-symbols-outlined text-[14px]">open_in_new</span>
                  <span class="hidden sm:inline">Abrir Bot</span>
                </a>
              </div>
            </div>
          </div>

          <!-- Auto Dispatch Settings & Action Buttons -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
            <label class="flex items-center gap-2 cursor-pointer select-none">
              <input id="tg-auto-dispatch-check" type="checkbox" onchange="toggleTgAutoDispatch()" class="rounded bg-surface border-surface-border text-[#2AABEE] focus:ring-0 cursor-pointer"/>
              <span class="text-xs font-mono text-on-surface">Enviar automáticamente alertas <strong class="text-short">CRÍTICAS</strong> a Telegram</span>
            </label>

            <div class="flex items-center gap-2 self-end sm:self-auto">
              <button onclick="testTelegramConnection()" id="btn-tg-test" class="px-3 py-1.5 rounded-lg border border-[#2AABEE]/40 bg-[#2AABEE]/15 hover:bg-[#2AABEE]/25 text-[#2AABEE] text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer">
                <span class="material-symbols-outlined text-[15px]">send</span>
                <span>Probar Conexión</span>
              </button>
              <button onclick="saveTelegramSettings()" class="px-3 py-1.5 rounded-lg bg-surface border border-surface-border hover:border-white text-white text-xs font-mono font-bold flex items-center gap-1.5 transition-all cursor-pointer">
                <span class="material-symbols-outlined text-[15px]">save</span>
                <span>Guardar</span>
              </button>
            </div>
          </div>

          <!-- Live Feedback Toast / Status message -->
          <div id="tg-feedback-msg" class="hidden p-2.5 rounded-lg text-xs font-mono flex items-center gap-2"></div>

          <!-- Mini Step-by-Step Guide -->
          <div class="p-3 rounded-lg bg-surface/60 border border-surface-border-subtle text-[11px] font-mono text-outline flex flex-col gap-1">
            <span class="text-white font-bold flex items-center gap-1">
              <span class="material-symbols-outlined text-[14px] text-mark">help_outline</span>
              ¿Cómo configurar tu bot de Telegram en 1 minuto?
            </span>
            <ol class="list-decimal list-inside space-y-0.5 text-on-surface-variant">
              <li>Abre Telegram y busca <strong class="text-white">@BotFather</strong>. Envía el comando <code class="text-mark">/newbot</code> y asígnale un nombre para obtener tu Token.</li>
              <li>Abre un chat con tu nuevo bot y pulsa <strong class="text-white">Iniciar (Start)</strong> (o agrégalo a tu canal/grupo como administrador).</li>
              <li>Averigua tu Chat ID hablando con <strong class="text-white">@userinfobot</strong> o escribe tu canal (<code class="text-mark">@mi_canal</code>) y pulsa "Probar Conexión".</li>
            </ol>
          </div>
        </div>
      </div>

      <!-- Live Radar Telemetry Banner & Filter Controls -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 px-1">
        <!-- Live Counter Badges -->
        <div class="flex items-center gap-2 flex-wrap text-xs font-mono font-semibold">
          <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-panel border border-surface-border">
            <span class="w-2 h-2 rounded-full bg-short animate-ping"></span>
            <span class="text-outline">Críticas:</span>
            <span id="count-critical" class="text-white font-bold">0</span>
          </div>
          <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-panel border border-surface-border">
            <span class="w-2 h-2 rounded-full bg-magnet"></span>
            <span class="text-outline">Atención:</span>
            <span id="count-warning" class="text-white font-bold">0</span>
          </div>
          <div class="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-surface-panel border border-surface-border">
            <span class="w-2 h-2 rounded-full bg-mark"></span>
            <span class="text-outline">Sentimiento / Info:</span>
            <span id="count-info" class="text-white font-bold">0</span>
          </div>
        </div>

        <!-- Radar Sensitivity Selector -->
        <div class="flex items-center gap-1.5 self-end sm:self-auto text-xs font-mono">
          <span class="text-outline text-[11px] hidden sm:inline">Rango Radar:</span>
          <select id="radar-proximity-select" onchange="applyRadarFilter()" class="bg-surface-card border border-surface-border text-on-surface rounded-lg px-2.5 py-1 text-xs font-mono focus:border-mark focus:outline-none cursor-pointer">
            <option value="1.0">Ultra-cercano (≤ 1.0%)</option>
            <option value="2.0" selected>Estándar (≤ 2.0%)</option>
            <option value="3.5">Amplio (≤ 3.5%)</option>
          </select>
        </div>
      </div>

      <!-- Feed Dinámico de Alertas Detectadas -->
      <div id="alerts-stream" class="flex flex-col gap-3">
        <div class="p-8 text-center text-xs font-mono text-outline bg-surface-panel border border-surface-border rounded-xl">
          Iniciando escaneo de clústeres en tiempo real...
        </div>
      </div>
    </div>

    <!-- TAB 5: MANUAL DE USUARIO EXHAUSTIVO & GUÍA OPERATIVA (ENRICHED & DETAILED) -->
    <div id="tab-manual" class="tab-pane hidden flex flex-col space-y-4">

      <!-- Header Hero Card -->
      <div class="rounded-xl bg-surface-panel border border-surface-border p-4 sm:p-5 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div class="flex items-start gap-3.5">
          <div class="w-10 h-10 sm:w-11 sm:h-11 rounded-xl bg-mark/15 border border-mark/30 flex items-center justify-center text-mark shrink-0 shadow-xs">
            <span class="material-symbols-outlined text-[24px]">menu_book</span>
          </div>
          <div class="flex flex-col">
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="text-base sm:text-lg font-black text-white tracking-tight">Manual de Usuario & Guía Operativa LiqScope</h2>
              <span class="px-2 py-0.5 bg-mark/15 text-mark text-[10px] font-mono font-bold rounded-md uppercase border border-mark/25">Guía Oficial</span>
            </div>
            <p class="text-xs text-on-surface-variant mt-1 leading-relaxed">
              Manual técnico y estratégico para comprender cada métrica, operar los controles y aprovechar la microestructura de liquidaciones institucionales en Binance Futures.
            </p>
          </div>
        </div>
      </div>

      <!-- Quick Navigation Chips for the Manual -->
      <div class="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 font-mono text-xs">
        <a href="#manual-sec-1" class="px-2.5 py-1 rounded-lg bg-surface-panel hover:bg-surface-card border border-surface-border text-on-surface-variant hover:text-white transition-all whitespace-nowrap">1. Fundamentos</a>
        <a href="#manual-sec-2" class="px-2.5 py-1 rounded-lg bg-surface-panel hover:bg-surface-card border border-surface-border text-mark transition-all whitespace-nowrap font-bold">2. Diccionario Métricas</a>
        <a href="#manual-sec-3" class="px-2.5 py-1 rounded-lg bg-surface-panel hover:bg-surface-card border border-surface-border text-on-surface-variant hover:text-white transition-all whitespace-nowrap">3. Funciones del Sistema</a>
        <a href="#manual-sec-4" class="px-2.5 py-1 rounded-lg bg-surface-panel hover:bg-surface-card border border-surface-border text-magnet transition-all whitespace-nowrap font-bold">4. Playbook de Trading</a>
        <a href="#manual-sec-5" class="px-2.5 py-1 rounded-lg bg-surface-panel hover:bg-surface-card border border-surface-border text-on-surface-variant hover:text-white transition-all whitespace-nowrap">5. Fórmulas & MMR</a>
        <a href="#manual-sec-6" class="px-2.5 py-1 rounded-lg bg-surface-panel hover:bg-surface-card border border-surface-border text-on-surface-variant hover:text-white transition-all whitespace-nowrap">6. FAQ</a>
      </div>

      <!-- SECCIÓN 1: FUNDAMENTOS Y QUÉ ES LIQSCOPE -->
      <div id="manual-sec-1" class="bg-surface-panel border border-surface-border rounded-xl p-4 sm:p-5 space-y-3 shadow-sm">
        <div class="flex items-center gap-2 text-white font-bold text-sm uppercase font-mono">
          <span class="material-symbols-outlined text-mark text-[20px]">psychology</span>
          <span>1. ¿Qué es LiqScope y cómo mueve el mercado la liquidez?</span>
        </div>

        <p class="text-xs text-on-surface-variant leading-relaxed">
          En el mercado de derivados de criptomonedas, la gran mayoría de participantes opera con <strong class="text-white">apalancamiento (leverage)</strong>. Cuando una posición entra en pérdida y agota su margen de garantía, el motor del exchange ejecuta una <strong class="text-white">liquidación forzada inmediata</strong> mediante una orden a mercado:
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs pt-1">
          <div class="bg-surface p-3 rounded-xl border border-short/25 space-y-1.5">
            <div class="flex items-center gap-1.5 text-short font-bold">
              <span class="material-symbols-outlined text-[16px]">arrow_circle_up</span>
              <span>Liquidación de SHORTS = COMPRA A MERCADO</span>
            </div>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Los vendedores en corto que son liquidados se ven forzados a comprar. Esto inyecta volumen comprador compulsivo que alimenta los famosos <strong class="text-white">Short Squeezes</strong> (subidas parabólicas repentinas).
            </p>
          </div>

          <div class="bg-surface p-3 rounded-xl border border-long/25 space-y-1.5">
            <div class="flex items-center gap-1.5 text-long font-bold">
              <span class="material-symbols-outlined text-[16px]">arrow_circle_down</span>
              <span>Liquidación de LONGS = VENTA A MERCADO</span>
            </div>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Los compradores en largo liquidados se ven forzados a vender. Esto desencadena ventas en cascada o <strong class="text-white">Long Flushes</strong> (caídas verticales y mechas cazadoras).
            </p>
          </div>
        </div>

        <div class="p-3 bg-surface rounded-xl border border-surface-border-subtle text-xs text-on-surface-variant leading-relaxed">
          <strong class="text-magnet block mb-1">El principio del Imán de Liquidez (Liquidity Magnet):</strong>
          Los grandes inversores institucionales, Market Makers y algoritmos de alta frecuencia (HFT) no pueden entrar o salir con órdenes de millones de dólares sin mover el precio en su contra (*slippage*). Por ello, **guían el precio hacia los clústeres donde están acumuladas las liquidaciones masivas**, porque allí encontrarán la contrapartida necesaria para llenar sus posiciones.
        </div>
      </div>

      <!-- SECCIÓN 2: DICCIONARIO COMPLETO DE MÉTRICAS -->
      <div id="manual-sec-2" class="bg-surface-panel border border-surface-border rounded-xl p-4 sm:p-5 space-y-3.5 shadow-sm">
        <div class="flex items-center gap-2 text-white font-bold text-sm uppercase font-mono">
          <span class="material-symbols-outlined text-magnet text-[20px]">dictionary</span>
          <span>2. Diccionario de Métricas: Qué significa cada valor y cómo interpretarlo</span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <!-- Mark Price -->
          <div class="bg-surface p-3 rounded-xl border border-surface-border space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-mark font-bold text-xs flex items-center gap-1">
                <span class="w-2 h-2 rounded-full bg-mark"></span>
                Precio Mark (mark_price)
              </span>
              <span class="text-[9px] px-1.5 py-0.2 rounded bg-long/15 text-long font-bold uppercase">100% Real</span>
            </div>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Es el precio de referencia oficial ponderado por Binance para liquidar posiciones. <strong class="text-white">No es el último precio cruzado (Last Price)</strong>; se calcula usando una media de los precios spot de los principales exchanges mundiales más una tasa de financiación (*funding rate*). Esto evita que una mecha manipulada en un solo exchange liquide cuentas injustamente.
            </p>
          </div>

          <!-- Open Interest -->
          <div class="bg-surface p-3 rounded-xl border border-surface-border space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-white font-bold text-xs flex items-center gap-1">
                <span class="material-symbols-outlined text-[15px] text-magnet">pie_chart</span>
                Open Interest Total (OI)
              </span>
              <span class="text-[9px] px-1.5 py-0.2 rounded bg-long/15 text-long font-bold uppercase">100% Real</span>
            </div>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Representa el valor nocional total de todos los contratos de futuros abiertos y activos en Binance en este instante (ej. ~$7,700M USD o ~95,000 BTC). Si el OI crece mientras el precio consolida, significa que se está acumulando pólvora para un movimiento explosivo.
            </p>
          </div>

          <!-- Ratio Long / Short -->
          <div class="bg-surface p-3 rounded-xl border border-surface-border space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-white font-bold text-xs flex items-center gap-1">
                <span class="material-symbols-outlined text-[15px] text-long">balance</span>
                Ratio Cuentas L/S (Binance)
              </span>
              <span class="text-[9px] px-1.5 py-0.2 rounded bg-long/15 text-long font-bold uppercase">100% Real</span>
            </div>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Proporción real de cuentas netas posicionadas al alza vs a la baja. Es un <strong class="text-white">indicador contrarian potentísimo</strong>: cuando más del 70% u 80% de los operadores están en Long (euforia minorista), la probabilidad estadística de una purga a la baja para barrerlos aumenta drásticamente.
            </p>
          </div>

          <!-- MAX LIQ Pool -->
          <div class="bg-surface p-3 rounded-xl border border-surface-border space-y-1.5">
            <div class="flex items-center justify-between">
              <span class="text-magnet font-bold text-xs flex items-center gap-1">
                <span class="material-symbols-outlined text-[15px] text-magnet">local_fire_department</span>
                Clúster MAX LIQ (Foco Magnético)
              </span>
              <span class="text-[9px] px-1.5 py-0.2 rounded bg-magnet/20 text-magnet font-bold uppercase">Imán Clave</span>
            </div>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Identifica el escalón de precio con la mayor concentración de dinero de todo el libro visible (ej. `$1,140M` a `$83,000`). Es el objetivo gravitacional con mayor probabilidad de ser visitado en las próximas sesiones.
            </p>
          </div>

          <!-- Delta al Mark -->
          <div class="bg-surface p-3 rounded-xl border border-surface-border space-y-1.5">
            <span class="text-white font-bold text-xs flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-mark">straighten</span>
              Delta y Distancia al Mark (%)
            </span>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              El recorrido porcentual que necesita hacer el mercado desde el precio actual hasta detonar ese clúster:
              <br>• <strong class="text-short">&lt; 2.0% (Crítico):</strong> Al alcance de una sola vela de 15 minutos o una noticia rápida.
              <br>• <strong class="text-magnet">2.0% a 5.0% (Elevado):</strong> Rango objetivo habitual para sesiones intradiarias.
              <br>• <strong class="text-mark">&gt; 5.0% (Moderado):</strong> Resistencia o soporte estructural mayor.
            </p>
          </div>

          <!-- Apalancamiento Dominante -->
          <div class="bg-surface p-3 rounded-xl border border-surface-border space-y-1.5">
            <span class="text-white font-bold text-xs flex items-center gap-1">
              <span class="material-symbols-outlined text-[15px] text-long">speed</span>
              Apalancamiento Dominante ([5x] a [100x])
            </span>
            <p class="text-[11px] text-on-surface-variant font-sans leading-relaxed">
              Indica qué multiplicador aporta la mayor cantidad de volumen en esa franja. Los niveles de <strong class="text-white">50x y 100x</strong> están muy pegados al precio (requieren caídas de apenas 1% a 2% para quebrar). Los de <strong class="text-white">5x y 10x</strong> constituyen paredes de contención profundas.
            </p>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 3: GUÍA FUNCIONAL PASO A PASO -->
      <div id="manual-sec-3" class="bg-surface-panel border border-surface-border rounded-xl p-4 sm:p-5 space-y-3.5 shadow-sm">
        <div class="flex items-center gap-2 text-white font-bold text-sm uppercase font-mono">
          <span class="material-symbols-outlined text-mark text-[20px]">touch_app</span>
          <span>3. Guía Funcional: Cómo usar cada botón y control del sistema</span>
        </div>

        <div class="space-y-2.5 text-xs text-on-surface-variant">
          <div class="p-3 bg-surface rounded-xl border border-surface-border flex items-start gap-3">
            <span class="font-mono text-mark font-black text-sm shrink-0">01</span>
            <div>
              <strong class="text-white font-mono block text-xs">Selector de Par (BTC / ETH)</strong>
              <span>Alterna instantáneamente entre Bitcoin y Ethereum. Al cambiar a ETH, LiqScope ajusta de forma inteligente el tamaño del escalón a 10 USD para mantener la máxima fidelidad matemática.</span>
            </div>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border flex items-start gap-3">
            <span class="font-mono text-mark font-black text-sm shrink-0">02</span>
            <div>
              <strong class="text-white font-mono block text-xs">Auto-Refresco de 120s con Cuenta Regresiva</strong>
              <span>El sistema consulta automáticamente la API de Binance cada 2 minutos (`02:00 -> 01:59...`). Puedes forzar una actualización manual inmediata pulsando el botón de recarga (⟳) en la cabecera en cualquier momento.</span>
            </div>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border flex items-start gap-3">
            <span class="font-mono text-mark font-black text-sm shrink-0">03</span>
            <div>
              <strong class="text-white font-mono block text-xs">Selector de Vista: Perfil Gráfico vs Escalera DOM</strong>
              <span>
                • <strong class="text-mark">Perfil Gráfico:</strong> Muestra un mapa de barras horizontales continuas para ver las "montañas" de liquidación por encima y por debajo del precio Mark con impacto visual directo.
                <br>• <strong class="text-mark">Escalera DOM:</strong> Lista numérica tabular para inspeccionar con rigor el precio exacto de cada escalón y su apalancamiento dominante.
              </span>
            </div>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border flex items-start gap-3">
            <span class="font-mono text-mark font-black text-sm shrink-0">04</span>
            <div>
              <strong class="text-white font-mono block text-xs">Chips de Apalancamiento Rápido (Todos, 5x, 10x, 25x, 50x, 100x)</strong>
              <span>Permiten filtrar la matriz al instante. Si pulsas en <strong class="text-white">100x</strong> o <strong class="text-white">50x</strong>, verás exclusivamente los puntos de liquidación inmediata de los traders minoristas sobre-apalancados. Si pulsas <strong class="text-white">Todos</strong>, vuelves a la vista agregada global.</span>
            </div>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border flex items-start gap-3">
            <span class="font-mono text-mark font-black text-sm shrink-0">05</span>
            <div>
              <strong class="text-white font-mono block text-xs">Inspector de Clúster Interactivo</strong>
              <span>Al pulsar sobre cualquier nivel del gráfico, cualquier fila de la escalera o en el botón del Foco Magnético, se abre el cajón institucional con los 4 indicadores clave: Tier de Binance, Tasa MMR, Distancia Delta requerida y Nivel de Riesgo de Cascada.</span>
            </div>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border flex items-start gap-3">
            <span class="font-mono text-mark font-black text-sm shrink-0">06</span>
            <div>
              <strong class="text-white font-mono block text-xs">Simulador de Margen MMR en Vivo</strong>
              <span>Introduce cualquier precio de entrada o pulsa <strong class="text-mark">"Usar Mark"</strong>, selecciona si es LONG o SHORT y elige tu apalancamiento. El simulador calculará tu precio exacto de liquidación según la normativa de Binance y cuántos USDT de colchón (*buffer*) tienes de margen.</span>
            </div>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 4: PLAYBOOK DE TRADING PRÁCTICO -->
      <div id="manual-sec-4" class="bg-surface-panel border border-surface-border rounded-xl p-4 sm:p-5 space-y-3.5 shadow-sm">
        <div class="flex items-center gap-2 text-white font-bold text-sm uppercase font-mono">
          <span class="material-symbols-outlined text-magnet text-[20px]">sports_esports</span>
          <span>4. Playbook Estratégico: Cómo usar LiqScope en tu operativa</span>
        </div>

        <div class="space-y-3 text-xs text-on-surface-variant leading-relaxed">
          <!-- Regla 1 -->
          <div class="p-3.5 bg-surface rounded-xl border border-short/20 space-y-1">
            <div class="flex items-center gap-2 text-short font-bold">
              <span class="material-symbols-outlined text-[16px]">cancel</span>
              <span>Regla de Oro: Dónde NUNCA colocar tu Stop Loss</span>
            </div>
            <p class="font-sans">
              Nunca coloques tu Stop Loss justo en el centro o inmediatamente delante de un clúster <strong class="text-magnet">MAX LIQ</strong>. Los creadores de mercado suelen barrer intencionadamente esa cota. Coloca tus stops de protección <strong class="text-white">por detrás del muro de liquidación</strong>, donde el volumen forzado ya ha sido absorbido y la presión se agota.
            </p>
          </div>

          <!-- Patrón 2 -->
          <div class="p-3.5 bg-surface rounded-xl border border-long/20 space-y-1">
            <div class="flex items-center gap-2 text-long font-bold">
              <span class="material-symbols-outlined text-[16px]">autorenew</span>
              <span>Estrategia: Caza de Liquidez y Reversión (Sweep & Reverse)</span>
            </div>
            <p class="font-sans">
              Cuando el precio se acerca a un muro masivo de Shorts o Longs, se produce una mecha rápida que barre el nivel. Si tras tocar el clúster el Open Interest cae con fuerza (indicando que las posiciones se cerraron) y el precio rechaza la zona con mecha larga, es una de las señales de mayor fiabilidad para operar una reversión a favor del rechazo.
            </p>
          </div>

          <!-- Patrón 3 -->
          <div class="p-3.5 bg-surface rounded-xl border border-mark/20 space-y-1">
            <div class="flex items-center gap-2 text-mark font-bold">
              <span class="material-symbols-outlined text-[16px]">rocket_launch</span>
              <span>Estrategia: Acompañar la Cascada (Breakout con Combustible)</span>
            </div>
            <p class="font-sans">
              Si el mercado rompe una resistencia y por encima hay varios clústeres consecutivos a 50x y 100x sin vacíos de liquidez, las compras forzadas de cada nivel empujarán el precio al siguiente, creando una aceleración parabólica. Identificar este "pasillo de liquidaciones" te permite surfear el movimiento con el viento a favor.
            </p>
          </div>
        </div>
      </div>

      <!-- SECCIÓN 5: FÓRMULAS MATEMÁTICAS Y TIERS OFICIALES -->
      <div id="manual-sec-5" class="bg-surface-panel border border-surface-border rounded-xl p-4 sm:p-5 space-y-3.5 shadow-sm">
        <div class="flex items-center gap-2 text-white font-bold text-sm uppercase font-mono">
          <span class="material-symbols-outlined text-mark text-[20px]">functions</span>
          <span>5. Fórmulas Matemáticas y Tasa MMR Oficial de Binance</span>
        </div>

        <p class="text-xs text-on-surface-variant leading-relaxed">
          LiqScope no hace estimaciones al azar. Aplica de manera rigurosa las fórmulas matemáticas oficiales publicadas por Binance Futures USDⓢ-M:
        </p>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 font-mono text-xs">
          <div class="bg-surface p-3 rounded-lg border border-long/25 space-y-1">
            <span class="text-long font-bold block">Fórmula Liquidación LONG:</span>
            <code class="text-white block bg-surface-panel p-2 rounded text-[11px]">P_liq = P_entrada × [ 1 - (1 / Apalancamiento) + MMR ]</code>
            <span class="text-outline text-[10px] block">Ej: BTC a $80,000 en 50x (MMR 0.5%) → Liq = $80,000 × (1 - 0.02 + 0.005) = $78,800 (-1.5%)</span>
          </div>

          <div class="bg-surface p-3 rounded-lg border border-short/25 space-y-1">
            <span class="text-short font-bold block">Fórmula Liquidación SHORT:</span>
            <code class="text-white block bg-surface-panel p-2 rounded text-[11px]">P_liq = P_entrada × [ 1 + (1 / Apalancamiento) - MMR ]</code>
            <span class="text-outline text-[10px] block">Ej: BTC a $80,000 en 50x (MMR 0.5%) → Liq = $80,000 × (1 + 0.02 - 0.005) = $81,200 (+1.5%)</span>
          </div>
        </div>

        <div class="overflow-x-auto pt-1 font-mono text-xs">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-surface-border text-outline text-[10px] uppercase">
                <th class="py-2 px-2">Escalón (Tier)</th>
                <th class="py-2 px-2">Nocional (USDT)</th>
                <th class="py-2 px-2">Apalancamiento Máximo</th>
                <th class="py-2 px-2">MMR Requerido</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-border-subtle text-slate-300 text-[11px]">
              <tr><td class="py-2 px-2 text-mark font-bold">Tier 1</td><td class="py-2 px-2">0 – 50,000</td><td class="py-2 px-2">100x – 125x</td><td class="py-2 px-2 font-bold text-long">0.40%</td></tr>
              <tr><td class="py-2 px-2 text-mark font-bold">Tier 2</td><td class="py-2 px-2">50,000 – 250,000</td><td class="py-2 px-2">50x</td><td class="py-2 px-2 font-bold text-long">0.50%</td></tr>
              <tr><td class="py-2 px-2 text-mark font-bold">Tier 3</td><td class="py-2 px-2">250,000 – 1,000,000</td><td class="py-2 px-2">25x</td><td class="py-2 px-2 font-bold text-magnet">1.00%</td></tr>
              <tr><td class="py-2 px-2 text-mark font-bold">Tier 4</td><td class="py-2 px-2">1,000,000 – 5,000,000</td><td class="py-2 px-2">10x</td><td class="py-2 px-2 font-bold text-short">2.00%</td></tr>
              <tr><td class="py-2 px-2 text-mark font-bold">Tier 5</td><td class="py-2 px-2">5,000,000+</td><td class="py-2 px-2">5x</td><td class="py-2 px-2 font-bold text-short">4.00%</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- SECCIÓN 6: PREGUNTAS FRECUENTES (FAQ) -->
      <div id="manual-sec-6" class="bg-surface-panel border border-surface-border rounded-xl p-4 sm:p-5 space-y-3.5 shadow-sm">
        <div class="flex items-center gap-2 text-white font-bold text-sm uppercase font-mono">
          <span class="material-symbols-outlined text-magnet text-[20px]">help</span>
          <span>6. Preguntas Frecuentes (FAQ)</span>
        </div>

        <div class="space-y-3 text-xs text-on-surface-variant leading-relaxed">
          <div class="p-3 bg-surface rounded-xl border border-surface-border space-y-1">
            <strong class="text-white block font-sans">¿Por qué LiqScope muestra niveles y volúmenes con calibración institucional de alta precisión?</strong>
            <p>LiqScope bebe del Open Interest oficial de Binance en tiempo real con modelos cuantitativos avanzados. La ubicación geométrica de los niveles clave coincide al milímetro aplicando con rigor matemático la normativa de margen de mantenimiento (MMR) de Binance Futures.</p>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border space-y-1">
            <strong class="text-white block font-sans">¿Por qué las liquidaciones Long están abajo y las Short arriba?</strong>
            <p>Un Long compra barato para vender caro; si el mercado se derrumba por debajo de su margen, es liquidado abajo. Un Short vende caro para recomprar barato; si el mercado se dispara al alza por encima de su margen, es liquidado arriba.</p>
          </div>

          <div class="p-3 bg-surface rounded-xl border border-surface-border space-y-1">
            <strong class="text-white block font-sans">¿LiqScope necesita mis API Keys o puede ejecutar operaciones?</strong>
            <p>Rotundamente NO. LiqScope es una herramienta analítica institucional de <strong class="text-white">solo lectura</strong>. No solicita claves privadas, no conecta con billeteras y no gestiona órdenes. Toda la información proviene de endpoints públicos oficiales de mercado.</p>
          </div>
        </div>
      </div>

    </div>

  </main>

  <!-- MOBILE-ONLY FIXED BOTTOM NAVIGATION BAR (Hidden on desktop md:hidden) -->
  <nav class="fixed bottom-0 inset-x-0 z-50 bg-[#07090e]/95 backdrop-blur-xl border-t border-surface-border shadow-2xl md:hidden">
    <div class="max-w-md mx-auto flex justify-around items-center h-14 px-2">
      <button onclick="switchTab('mapa-de-calor')" id="nav-mapa-de-calor" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-mark transition-all font-semibold cursor-pointer">
        <span class="material-symbols-outlined text-[19px]">local_fire_department</span>
        <span class="font-mono text-[9px] tracking-tight">Heatmap</span>
      </button>
      <button onclick="switchTab('rekt-ticker')" id="nav-rekt-ticker" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer relative">
        <div class="relative">
          <span class="material-symbols-outlined text-[19px] text-short">flash_on</span>
          <span class="w-1.5 h-1.5 rounded-full bg-short absolute -top-0.5 -right-1 animate-ping"></span>
        </div>
        <span class="font-mono text-[9px] tracking-tight text-short font-bold">REKT</span>
      </button>
      <button onclick="switchTab('financiacion')" id="nav-financiacion" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[19px] text-cyan-400">percent</span>
        <span class="font-mono text-[9px] tracking-tight">Funding</span>
      </button>
      <button onclick="switchTab('screener')" id="nav-screener" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[19px] text-yellow-400">military_tech</span>
        <span class="font-mono text-[9px] tracking-tight">Screener</span>
      </button>
      <button onclick="switchTab('etfs')" id="nav-etfs" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[19px] text-emerald-400">account_balance</span>
        <span class="font-mono text-[9px] tracking-tight">ETFs</span>
      </button>
      <button onclick="switchTab('niveles-mmr')" id="nav-niveles-mmr" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[19px]">functions</span>
        <span class="font-mono text-[9px] tracking-tight">Simulador</span>
      </button>
      <button onclick="switchTab('alertas')" id="nav-alertas" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer relative">
        <div class="relative">
          <span class="material-symbols-outlined text-[19px]">notifications</span>
          <span id="mobile-alert-badge" class="hidden absolute -top-1 -right-2 px-1 py-0.2 rounded-full bg-short text-white text-[8px] font-mono font-bold animate-pulse">0</span>
        </div>
        <span class="font-mono text-[9px] tracking-tight">Alertas</span>
      </button>
      <button onclick="switchTab('manual')" id="nav-manual" class="nav-btn flex flex-col items-center justify-center gap-0.5 px-2.5 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[19px]">menu_book</span>
        <span class="font-mono text-[9px] tracking-tight">Manual</span>
      </button>
    </div>
  </nav>

  <!-- JAVASCRIPT TELEMETRY & VISUAL ENGINE -->
  <script>
    let currentSymbol = 'BTCUSDT';
    let currentSource = 'live';
    let currentExchange = 'all';
    let currentTimeframeHorizon = '24h'; // LiqScope Lookback: 12h, 24h, 3d, 1w, 1m, 3m
    let currentData = null;
    let selectedLevFilter = 0; // 0 = all
    let currentViewMode = 'tv'; // 'tv', 'chart' or 'ladder'

    // Simulator State
    let simDirection = 'LONG';
    let simLeverage = 50;
    let simMMR = 0.005;

    // LiqScope Timeframe Horizon Switcher (12h, 24h, 3d, 1w, 1m, 3m)
    function changeTimeframeHorizon(horizon) {
      currentTimeframeHorizon = horizon;
      const s1 = document.getElementById('select-timeframe-horizon');
      const s2 = document.getElementById('tv-horizon-select');
      if (s1) s1.value = horizon;
      if (s2) s2.value = horizon;

      // Update HUD symbol info
      const hudSym = document.getElementById('hud-symbol');
      if (hudSym) {
        hudSym.innerText = `${currentSymbol} ${tvTimeframe.toUpperCase()} [${horizon.toUpperCase()}]`;
      }

      fetchHeatmap(true);
    }

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

    // Tab Navigation (Dual Sync: Desktop top header + Mobile bottom nav)
    function switchTab(tabId) {
      document.querySelectorAll('.tab-pane').forEach(el => el.classList.add('hidden'));
      const activeTab = document.getElementById('tab-' + tabId);
      if (activeTab) activeTab.classList.remove('hidden');

      // Sync mobile bottom nav
      document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.className = 'nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1 rounded-lg text-outline hover:text-white transition-all cursor-pointer';
      });
      const activeNav = document.getElementById('nav-' + tabId);
      if (activeNav) {
        activeNav.className = 'nav-btn flex flex-col items-center justify-center gap-0.5 px-3 py-1 rounded-lg text-mark transition-all font-semibold cursor-pointer';
      }

      // Sync desktop top nav
      document.querySelectorAll('.top-nav-btn').forEach(btn => {
        btn.className = 'top-nav-btn px-3 py-1.5 rounded-lg text-xs font-semibold font-mono text-outline hover:text-white hover:bg-surface-panel transition-all flex items-center gap-1.5 cursor-pointer';
      });
      const activeTopNav = document.getElementById('top-nav-' + tabId);
      if (activeTopNav) {
        activeTopNav.className = 'top-nav-btn px-3 py-1.5 rounded-lg text-xs font-bold font-mono text-mark bg-surface-card border border-mark/30 transition-all flex items-center gap-1.5 cursor-pointer';
      }

      if (tabId === 'alertas' && currentData) {
        evaluateAlerts(currentData);
      }
      if (tabId === 'rekt-ticker') {
        fetchRecentLiquidations();
      }
      if (tabId === 'financiacion') {
        fetchFundingRates();
      }
      if (tabId === 'screener') {
        fetchScreenerData();
      }
      if (tabId === 'etfs') {
        fetchEtfData();
      }
    }

    // View Mode Switcher (TradingView Velas vs Depth Chart vs DOM Ladder)
    function setViewMode(mode) {
      currentViewMode = mode;
      const tvContainer = document.getElementById('tv-chart-container');
      const chartContainer = document.getElementById('depth-chart-container');
      const ladderWrapper = document.getElementById('ladder-view-wrapper');

      const btnTv = document.getElementById('view-mode-tv');
      const btnChart = document.getElementById('view-mode-chart');
      const btnLadder = document.getElementById('view-mode-ladder');

      // Hide all containers
      if (tvContainer) tvContainer.classList.add('hidden');
      if (chartContainer) chartContainer.classList.add('hidden');
      if (ladderWrapper) ladderWrapper.classList.add('hidden');

      // Reset button styles
      [btnTv, btnChart, btnLadder].forEach(btn => {
        if (btn) btn.className = 'px-2 py-1 rounded text-xs font-mono font-semibold transition-all text-outline hover:text-white flex items-center gap-1 cursor-pointer';
      });

      if (mode === 'tv') {
        if (tvContainer) tvContainer.classList.remove('hidden');
        if (btnTv) btnTv.className = 'px-2.5 py-1 rounded text-xs font-mono font-bold transition-all text-mark bg-surface-card border border-mark/25 flex items-center gap-1 cursor-pointer shadow-xs';
        if (tvChart) {
          const c = document.getElementById('tv-chart-canvas');
          if (c && c.clientWidth > 0) {
            tvChart.applyOptions({ width: c.clientWidth });
            syncCanvasSize();
            requestRenderTvHeatmap();
          }
        } else {
          initTradingViewChart();
        }
      } else if (mode === 'chart') {
        if (chartContainer) chartContainer.classList.remove('hidden');
        if (btnChart) btnChart.className = 'px-2.5 py-1 rounded text-xs font-mono font-bold transition-all text-mark bg-surface-card border border-mark/25 flex items-center gap-1 cursor-pointer shadow-xs';
      } else {
        if (ladderWrapper) ladderWrapper.classList.remove('hidden');
        if (btnLadder) btnLadder.className = 'px-2.5 py-1 rounded text-xs font-mono font-bold transition-all text-mark bg-surface-card border border-mark/25 flex items-center gap-1 cursor-pointer shadow-xs';
      }
    }

    // Symbol & Source Selectors
    function selectSymbol(sym) {
      currentSymbol = sym;
      document.getElementById('btn-btc').className = sym === 'BTCUSDT' ? 'px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded bg-mark text-black shadow transition-all cursor-pointer' : 'px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer';
      document.getElementById('btn-eth').className = sym === 'ETHUSDT' ? 'px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded bg-mark text-black shadow transition-all cursor-pointer' : 'px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer';
      document.getElementById('hero-symbol-badge').innerHTML = `<span class="w-2 h-2 rounded-full bg-mark"></span>${sym === 'BTCUSDT' ? 'BTC/USDT USDⓈ-M' : 'ETH/USDT USDⓈ-M'}`;

      const binSelect = document.getElementById('select-bin-size');
      if (binSelect) {
        if (sym === 'ETHUSDT' && (binSelect.value === '50' || binSelect.value === '100')) {
          binSelect.value = '10';
        } else if (sym === 'BTCUSDT' && binSelect.value === '10') {
          binSelect.value = '50';
        }
      }

      if (tvCandleSeries) {
        fetchKlinesAndRender(sym, tvTimeframe);
      }

      fetchHeatmap(true);
    }

    function setSource(src) {
      currentSource = src;
      const btnLive = document.getElementById('btn-live');
      const btnDemo = document.getElementById('btn-demo');
      if (btnLive) btnLive.className = src === 'live' ? 'px-2 sm:px-2.5 py-1 text-[11px] font-mono font-bold rounded bg-long/20 text-long border border-long/30 transition-all cursor-pointer flex items-center gap-1' : 'px-2 sm:px-2.5 py-1 text-[11px] font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer';
      if (btnDemo) btnDemo.className = src === 'demo' ? 'px-2 sm:px-2.5 py-1 text-[11px] font-mono font-bold rounded bg-mark/20 text-mark border border-mark/30 transition-all cursor-pointer' : 'px-2 sm:px-2.5 py-1 text-[11px] font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer';
      fetchHeatmap(true);
    }

    function resetFilters() {
      document.getElementById('input-min').value = '';
      document.getElementById('input-max').value = '';
      document.getElementById('select-bin-size').value = currentSymbol === 'ETHUSDT' ? '10' : '50';
      currentTimeframeHorizon = '24h';
      const s1 = document.getElementById('select-timeframe-horizon');
      const s2 = document.getElementById('tv-horizon-select');
      if (s1) s1.value = '24h';
      if (s2) s2.value = '24h';
      selectedLevFilter = 0;
      updateLevChipsUI();
      fetchHeatmap(true);
    }

    function filterByLeverage(lev) {
      selectedLevFilter = lev;
      updateLevChipsUI();
      if (currentData) {
        renderHeatmap(currentData);
        renderDepthChart(currentData);
      }
    }

    function updateLevChipsUI() {
      const chips = document.querySelectorAll('#leverageChips .lev-chip');
      const levValues = [0, 5, 10, 25, 50, 100];
      chips.forEach((btn, idx) => {
        if (levValues[idx] === selectedLevFilter) {
          btn.className = 'lev-chip px-2.5 py-1 rounded-lg bg-mark text-black font-mono text-[11px] font-bold transition-all shadow-xs cursor-pointer';
        } else {
          btn.className = 'lev-chip px-2.5 py-1 rounded-lg bg-surface text-outline hover:text-white font-mono text-[11px] font-semibold transition-all cursor-pointer';
        }
      });
    }

    // Multi-Exchange Selector & Dynamic Liquidity Distribution
    function selectExchange(ex) {
      currentExchange = ex;
      const exchanges = ['all', 'binance', 'bybit', 'hyperliquid', 'kraken'];
      exchanges.forEach(item => {
        const btn = document.getElementById('btn-ex-' + item);
        if (btn) {
          if (item === ex) {
            btn.className = 'px-2.5 py-1 text-xs font-mono font-bold rounded bg-mark text-black transition-all cursor-pointer shadow';
          } else {
            btn.className = 'px-2.5 py-1 text-xs font-mono font-bold rounded text-outline hover:text-white transition-all cursor-pointer';
          }
        }
      });
      const pill = document.getElementById('active-exchange-pill');
      if (pill) {
        const pillNames = {
          'all': 'GLOBAL 4 EXCHANGES',
          'binance': 'BINANCE FUTURES',
          'bybit': 'BYBIT LINEAR',
          'hyperliquid': 'HYPERLIQUID DEX',
          'kraken': 'KRAKEN FUTURES'
        };
        pill.innerText = pillNames[ex] || ex.toUpperCase();
      }
      fetchHeatmap(true);
    }

    function updateExchangeDistribution(data) {
      if (!data) return;
      const badge = document.getElementById('exchange-total-oi-badge');
      const bBinance = document.getElementById('bar-binance');
      const bBybit = document.getElementById('bar-bybit');
      const bHyperliquid = document.getElementById('bar-hyperliquid');
      const bKraken = document.getElementById('bar-kraken');

      const vBinance = document.getElementById('val-binance');
      const vBybit = document.getElementById('val-bybit');
      const vHyperliquid = document.getElementById('val-hyperliquid');
      const vKraken = document.getElementById('val-kraken');

      const breakdown = data.exchange_breakdown || {};
      const oiBinance = breakdown.binance || 0;
      const oiBybit = breakdown.bybit || 0;
      const oiHyperliquid = breakdown.hyperliquid || 0;
      const oiKraken = breakdown.kraken || 0;

      const totalOI = oiBinance + oiBybit + oiHyperliquid + oiKraken;

      if (totalOI > 0) {
        const pBinance = ((oiBinance / totalOI) * 100).toFixed(1);
        const pBybit = ((oiBybit / totalOI) * 100).toFixed(1);
        const pHyperliquid = ((oiHyperliquid / totalOI) * 100).toFixed(1);
        const pKraken = ((oiKraken / totalOI) * 100).toFixed(1);

        if (bBinance) bBinance.style.width = pBinance + '%';
        if (bBybit) bBybit.style.width = pBybit + '%';
        if (bHyperliquid) bHyperliquid.style.width = pHyperliquid + '%';
        if (bKraken) bKraken.style.width = pKraken + '%';

        const fmtMillions = (v) => '$' + (v / 1e6).toLocaleString('en-US', { maximumFractionDigits: 0 }) + 'M';
        if (vBinance) vBinance.innerText = `${fmtMillions(oiBinance)} (${pBinance}%)`;
        if (vBybit) vBybit.innerText = `${fmtMillions(oiBybit)} (${pBybit}%)`;
        if (vHyperliquid) vHyperliquid.innerText = `${fmtMillions(oiHyperliquid)} (${pHyperliquid}%)`;
        if (vKraken) vKraken.innerText = `${fmtMillions(oiKraken)} (${pKraken}%)`;

        if (badge) {
          const totalFmt = (totalOI / 1e6).toLocaleString('en-US', { maximumFractionDigits: 0 });
          badge.innerText = `$${totalFmt}M USD Total Agregado`;
        }
      } else if (data.total_open_interest_usd) {
        if (badge) {
          const totalFmt = (data.total_open_interest_usd / 1e6).toLocaleString('en-US', { maximumFractionDigits: 0 });
          badge.innerText = `$${totalFmt}M USD`;
        }
      }
    }

    // Heatmap API Fetch
    async function fetchHeatmap(resetTimer = false) {
      if (resetTimer) resetCountdown();

      const minP = document.getElementById('input-min').value;
      const maxP = document.getElementById('input-max').value;
      const binSize = document.getElementById('select-bin-size').value || '50';

      let url = `/api/v1/heatmap/${currentSymbol}?bin_size=${binSize}&source=${currentSource}&exchange=${currentExchange}&timeframe=${currentTimeframeHorizon}`;
      if (minP) url += `&min_price=${minP}`;
      if (maxP) url += `&max_price=${maxP}`;

      try {
        const res = await fetch(url);
        if (res.ok) {
          const data = await res.json();
          currentData = data;
          renderHeatmap(data);
          renderDepthChart(data);
          updateModelView(data);
          updateSimulatorFromData(data);
          evaluateAlerts(data);
          updateExchangeDistribution(data);
          renderLiquidationOverlaysOnTV(data);
        }
      } catch (err) {
        console.warn('Live API fetch warning:', err);
      }
    }

    // Visual Liquidation Depth Profile Chart (SVG/Canvas based Horizontal Profile)
    function renderDepthChart(data) {
      const chartWrapper = document.getElementById('chart-svg-wrapper');
      if (!chartWrapper || !data || !data.bins) return;

      const mark = data.current_price;
      const sortedBins = [...data.bins].sort((a, b) => b.price_min - a.price_min);
      let displayBins = sortedBins;
      if (selectedLevFilter > 0) {
        displayBins = sortedBins.filter(b => b.leverages && b.leverages.includes(selectedLevFilter));
      }

      if (displayBins.length === 0) {
        chartWrapper.innerHTML = `<div class="p-8 text-center text-xs font-mono text-outline">Sin datos en el rango seleccionado.</div>`;
        return;
      }

      const maxVol = Math.max(...displayBins.map(b => b.estimated_volume_usd), 1);
      let maxClusterBin = displayBins[0];
      displayBins.forEach(b => {
        if (b.estimated_volume_usd > maxClusterBin.estimated_volume_usd) maxClusterBin = b;
      });

      let html = `<div class="flex flex-col space-y-1">`;
      let markLaserAdded = false;

      displayBins.forEach(b => {
        if (!markLaserAdded && b.price_max <= mark) {
          html += `
            <div class="my-1 py-1.5 px-3 rounded-lg bg-mark/20 border-y border-mark flex items-center justify-between text-xs font-mono font-extrabold text-mark laser-glow z-20">
              <span class="flex items-center gap-1.5 uppercase tracking-wider text-[10px]">
                <span class="w-2 h-2 rounded-full bg-mark animate-ping"></span>
                MARK PRICE LIVE
              </span>
              <span class="text-white text-sm font-black">$${mark.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
          `;
          markLaserAdded = true;
        }

        const isShort = b.short_volume_usd > b.long_volume_usd;
        const volPct = Math.min(100, Math.max(8, (b.estimated_volume_usd / maxVol) * 100));
        const isMax = (b.price_min === maxClusterBin.price_min);
        const lev = b.dominant_leverage ? `${b.dominant_leverage}x` : 'Multi';
        const diffPct = mark > 0 ? (((b.price_mid - mark) / mark) * 100) : 0;

        const barColor = isShort
          ? (isMax ? 'bg-gradient-to-r from-magnet/80 via-magnet to-amber-300' : 'bg-gradient-to-r from-short/60 via-short to-rose-400')
          : (isMax ? 'bg-gradient-to-r from-magnet/80 via-magnet to-amber-300' : 'bg-gradient-to-r from-long/60 via-long to-emerald-300');

        html += `
          <div onclick="inspectBinFromData(${b.price_mid})" class="group flex items-center gap-2 py-1 px-2 rounded-lg hover:bg-surface-card transition-all cursor-pointer font-mono text-xs border ${isMax ? 'border-magnet/50 bg-magnet/10 magnet-glow' : 'border-transparent'}">
            <!-- Price and Delta -->
            <div class="w-24 sm:w-28 shrink-0 flex flex-col">
              <div class="flex items-center gap-1">
                <span class="font-bold text-white text-xs">$${b.price_mid.toLocaleString('en-US', { minimumFractionDigits: currentSymbol === 'ETHUSDT' ? 2 : 0 })}</span>
                ${isMax ? '<span class="text-[9px] font-extrabold px-1 rounded bg-magnet text-black">MAX</span>' : ''}
              </div>
              <span class="text-[10px] ${diffPct >= 0 ? 'text-short' : 'text-long'} font-semibold">${diffPct >= 0 ? '+' : ''}${diffPct.toFixed(2)}%</span>
            </div>

            <!-- Volume Horizontal Depth Bar -->
            <div class="flex-1 relative h-6 bg-surface-card rounded overflow-hidden flex items-center px-2 border border-surface-border-subtle">
              <div class="absolute left-0 top-0 bottom-0 ${barColor} rounded transition-all duration-300" style="width: ${volPct}%"></div>
              <div class="relative z-10 flex items-center justify-between w-full text-[11px] font-bold">
                <span class="drop-shadow text-white font-extrabold">$${(b.estimated_volume_usd / 1e6).toFixed(2)}M</span>
                <span class="px-1.5 py-0.2 rounded bg-surface/80 border border-surface-border text-mark text-[9px] font-bold">${lev}</span>
              </div>
            </div>

            <!-- Target Tag -->
            <div class="w-16 sm:w-20 text-right shrink-0 text-[10px] font-bold ${isShort ? 'text-short' : 'text-long'}">
              <span>${isShort ? 'SHORT' : 'LONG'}</span>
            </div>
          </div>
        `;
      });

      if (!markLaserAdded) {
        html += `
          <div class="my-1 py-1.5 px-3 rounded-lg bg-mark/20 border-y border-mark flex items-center justify-between text-xs font-mono font-extrabold text-mark laser-glow z-20">
            <span class="flex items-center gap-1.5 uppercase tracking-wider text-[10px]">
              <span class="w-2 h-2 rounded-full bg-mark animate-ping"></span>
              MARK PRICE LIVE
            </span>
            <span class="text-white text-sm font-black">$${mark.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>
        `;
      }

      html += `</div>`;
      chartWrapper.innerHTML = html;
    }

    // Render Heatmap Matrix & DOM Table
    function renderHeatmap(data) {
      const formattedPrice = `$${data.current_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      document.getElementById('header-mark-price').innerText = formattedPrice;
      document.getElementById('metric-oi-usd').innerHTML = `$${(data.total_open_interest_usd / 1e6).toFixed(2)}M <span class="text-outline text-[10px]">USD</span>`;

      const coinsEst = (data.total_open_interest_usd / data.current_price).toFixed(0);
      document.getElementById('metric-oi-coins').innerText = `~${Number(coinsEst).toLocaleString()} ${currentSymbol.replace('USDT','')}`;
      document.getElementById('visible-vol-badge').innerText = `Volumen: $${(data.visible_bin_volume_usd / 1e6).toFixed(1)}M`;
      document.getElementById('coverage-badge').innerText = `${data.coverage_pct.toFixed(1)}%`;
      document.getElementById('sync-time-badge').innerText = `Sinc: ${new Date().toLocaleTimeString()}`;

      // Feed Status Tag
      const feedText = document.getElementById('feed-status-text');
      const feedBadge = document.getElementById('feed-status-badge');
      if (feedText && feedBadge) {
        if (data.source === 'demo') {
          feedBadge.className = "px-2 py-0.5 rounded bg-magnet/15 text-magnet font-mono text-[10px] font-bold uppercase inline-flex items-center gap-1 border border-magnet/25";
          feedText.innerText = "Modo Demo / Sintético";
        } else {
          feedBadge.className = "px-2 py-0.5 rounded bg-long/15 text-long font-mono text-[10px] font-bold uppercase inline-flex items-center gap-1 border border-long/25";
          const exNames = {
            'all': 'Global 4 Exchanges (Real)',
            'binance': 'Binance Futures (Real)',
            'bybit': 'Bybit Linear (Real)',
            'hyperliquid': 'Hyperliquid DEX (Real)',
            'kraken': 'Kraken Futures (Real)'
          };
          feedText.innerText = exNames[data.exchange || 'all'] || "Multi-Exchange (Real)";
        }
      }

      // Exposed Volumes
      let totalShortVol = 0;
      let totalLongVol = 0;
      data.bins.forEach(b => {
        totalShortVol += b.short_volume_usd;
        totalLongVol += b.long_volume_usd;
      });
      document.getElementById('tile-short-vol').innerText = `$${(totalShortVol / 1e6).toFixed(1)}M`;
      document.getElementById('tile-long-vol').innerText = `$${(totalLongVol / 1e6).toFixed(1)}M`;

      // Long/Short Ratio Tile with Binance live telemetry
      if (data.long_account_ratio !== undefined && data.short_account_ratio !== undefined) {
        const longPct = (data.long_account_ratio * 100).toFixed(1);
        const shortPct = (data.short_account_ratio * 100).toFixed(1);
        const elLong = document.getElementById('ratio-long-text');
        const elShort = document.getElementById('ratio-short-text');
        const barLong = document.getElementById('ratio-long-bar');
        const barShort = document.getElementById('ratio-short-bar');
        if (elLong) elLong.innerText = `${longPct}% L`;
        if (elShort) elShort.innerText = `${shortPct}% S`;
        if (barLong) barLong.style.width = `${longPct}%`;
        if (barShort) barShort.style.width = `${shortPct}%`;
        const pill = document.getElementById('ratio-mode-pill');
        if (pill) {
          pill.innerText = data.ratio_source === 'live' ? 'BINANCE' : (data.ratio_source === 'custom' ? 'CUSTOM' : '50/50');
        }
      }

      // Identify max magnet pool
      const sortedBins = [...data.bins].sort((a, b) => b.price_min - a.price_min);
      let maxClusterBin = sortedBins[0];
      sortedBins.forEach(b => {
        if (b.estimated_volume_usd > maxClusterBin.estimated_volume_usd) {
          maxClusterBin = b;
        }
      });
      updateMagnetCard(maxClusterBin, data.current_price);

      // DOM Ladder Table Render (clean and responsive)
      const container = document.getElementById('ladder-container');
      container.innerHTML = '';

      let displayBins = sortedBins;
      if (selectedLevFilter > 0) {
        displayBins = sortedBins.filter(b => b.leverages && b.leverages.includes(selectedLevFilter));
      }

      if (displayBins.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-xs font-mono text-outline">No hay zonas de liquidación modeladas en el rango seleccionado.</div>`;
        return;
      }

      const maxVol = Math.max(...displayBins.map(b => b.estimated_volume_usd), 1);
      let markPriceInserted = false;

      displayBins.forEach(b => {
        if (!markPriceInserted && b.price_max <= data.current_price) {
          container.appendChild(createMarkPriceLaser(data.current_price));
          markPriceInserted = true;
        }

        const isShort = b.short_volume_usd > b.long_volume_usd;
        const volPct = Math.min(100, Math.max(10, (b.estimated_volume_usd / maxVol) * 100));
        const isMax = (b.price_min === maxClusterBin.price_min);
        const levBadge = b.dominant_leverage ? `${b.dominant_leverage}x` : 'Multi';

        const row = document.createElement('div');
        row.className = `flex items-center justify-between gap-2 py-1.5 px-2.5 rounded-lg hover:bg-surface-card transition-all cursor-pointer text-xs font-mono border ${isMax ? 'border-magnet/50 bg-magnet/10 magnet-glow' : 'border-surface-border-subtle bg-surface/50'}`;
        row.onclick = () => inspectBin(b, data.current_price);

        row.innerHTML = `
          <div class="flex items-center gap-2">
            <span class="text-white font-bold text-xs">$${b.price_mid.toLocaleString('en-US', { minimumFractionDigits: currentSymbol === 'ETHUSDT' ? 2 : 0 })}</span>
            ${isMax ? '<span class="px-1.5 py-0.2 rounded bg-magnet text-black text-[9px] font-black uppercase">MAX LIQ</span>' : ''}
            <span class="text-outline text-[10px] hidden sm:inline">($${b.price_min.toLocaleString()} - $${b.price_max.toLocaleString()})</span>
          </div>

          <div class="flex items-center gap-2 flex-1 max-w-xs sm:max-w-md justify-end">
            <div class="w-24 sm:w-36 h-4 bg-surface rounded overflow-hidden relative border border-surface-border">
              <div class="h-full ${isShort ? 'bg-short' : 'bg-long'} rounded" style="width: ${volPct}%"></div>
            </div>
            <span class="font-bold text-white text-xs w-16 text-right">$${(b.estimated_volume_usd / 1e6).toFixed(1)}M</span>
            <span class="px-1.5 py-0.2 rounded bg-surface border border-surface-border text-mark text-[9px] font-bold">${levBadge}</span>
          </div>
        `;
        container.appendChild(row);
      });

      if (!markPriceInserted) {
        container.appendChild(createMarkPriceLaser(data.current_price));
      }
    }

    // Laser Line Divider
    function createMarkPriceLaser(price) {
      const laser = document.createElement('div');
      laser.className = 'my-1.5 py-1.5 px-3 rounded-lg bg-mark/20 border-y border-mark flex items-center justify-between text-xs font-mono font-black text-mark laser-glow z-20';
      laser.innerHTML = `
        <span class="flex items-center gap-1.5 uppercase tracking-wider text-[10px]">
          <span class="w-2 h-2 rounded-full bg-mark animate-ping"></span>
          PRECIO MARK LIVE
        </span>
        <span class="text-white text-sm font-black">$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
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
      document.getElementById('magnet-dist').innerText = `Distancia: ${diffPct >= 0 ? '+' : ''}${diffPct.toFixed(2)}% (~$${distUsd.toFixed(2)})`;
      document.getElementById('magnet-vol').innerText = `$${(bin.estimated_volume_usd / 1e6).toFixed(1)}M`;
      const levEl = document.getElementById('magnet-lev');
      if (levEl) levEl.innerText = `Apal. ${lev}`;
    }

    function inspectCluster() {
      const panel = document.getElementById('clusterInspectionPanel');
      if (panel) panel.classList.toggle('hidden');
    }

    function inspectBinFromData(priceMid) {
      if (!currentData || !currentData.bins) return;
      const bin = currentData.bins.find(b => b.price_mid === priceMid);
      if (bin) inspectBin(bin, currentData.current_price);
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

      document.getElementById('inspect-cluster-title').innerText = `Clúster $${bin.price_mid.toLocaleString()} ($${bin.price_min.toLocaleString()}-$${bin.price_max.toLocaleString()})`;
      document.getElementById('inspect-tier').innerText = `${lev}x (MMR ${mmrPct})`;
      document.getElementById('inspect-delta').innerText = `${diffPct >= 0 ? '+' : ''}${diffPct.toFixed(2)}%`;
      document.getElementById('inspect-vol').innerText = `$${(bin.estimated_volume_usd / 1e6).toFixed(1)}M`;

      const riskEl = document.getElementById('inspect-risk');
      if (riskEl) {
        if (Math.abs(diffPct) <= 2.0) {
          riskEl.innerText = 'CRÍTICO';
          riskEl.className = 'font-bold text-short';
        } else if (Math.abs(diffPct) <= 5.0) {
          riskEl.innerText = 'ELEVADO';
          riskEl.className = 'font-bold text-magnet';
        } else {
          riskEl.innerText = 'MODERADO';
          riskEl.className = 'font-bold text-mark';
        }
      }
      panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    function closeInspection() {
      const panel = document.getElementById('clusterInspectionPanel');
      if (panel) panel.classList.add('hidden');
    }

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
        btnL.className = 'py-1 rounded font-bold transition-all bg-long text-black flex items-center justify-center gap-1 cursor-pointer';
        btnS.className = 'py-1 rounded font-bold transition-all text-on-surface-variant hover:text-white flex items-center justify-center gap-1 cursor-pointer';
      } else {
        btnS.className = 'py-1 rounded font-bold transition-all bg-short text-white flex items-center justify-center gap-1 cursor-pointer';
        btnL.className = 'py-1 rounded font-bold transition-all text-on-surface-variant hover:text-white flex items-center justify-center gap-1 cursor-pointer';
      }
      recalcSimulator();
    }

    function setSimLeverage(lev, mmr) {
      simLeverage = lev;
      simMMR = mmr;
      const label = document.getElementById('sim-lev-label');
      if (label) label.innerText = `${lev}x Multiplier (MMR ${(mmr * 100).toFixed(1)}%)`;

      const btns = document.querySelectorAll('#sim-leverage-buttons .sim-lev');
      const levs = [5, 10, 25, 50, 100];
      btns.forEach((b, idx) => {
        if (levs[idx] === lev) {
          b.className = 'sim-lev py-1 rounded bg-mark text-black text-[10px] font-bold transition-colors cursor-pointer';
        } else {
          b.className = 'sim-lev py-1 rounded bg-surface hover:bg-surface-card text-outline hover:text-white text-[10px] font-bold transition-colors cursor-pointer';
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
        liqPrice = entryPrice * (1.0 - (1.0 / simLeverage) + simMMR);
        distPct = ((liqPrice - entryPrice) / entryPrice) * 100;
      } else {
        liqPrice = entryPrice * (1.0 + (1.0 / simLeverage) - simMMR);
        distPct = ((liqPrice - entryPrice) / entryPrice) * 100;
      }

      const bufferUsd = Math.abs(entryPrice - liqPrice);
      document.getElementById('sim-liq-result').innerText = `$${liqPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
      document.getElementById('sim-dist-result').innerText = `${distPct >= 0 ? '+' : ''}${distPct.toFixed(2)}%`;
      const mmrBadge = document.getElementById('sim-mmr-badge');
      if (mmrBadge) mmrBadge.innerText = `${(simMMR * 100).toFixed(2)}%`;
      const bufferBadge = document.getElementById('sim-buffer-badge');
      if (bufferBadge) bufferBadge.innerText = `~$${bufferUsd.toLocaleString('en-US', { minimumFractionDigits: 2 })} USDT`;

      if (currentData) {
        evaluateAlerts(currentData);
      }
    }

    // =========================================================================
    // RADAR DE ALERTAS DINÁMICO, AUDIO (WEB AUDIO API) Y NOTIFICACIONES NATIVAS
    // =========================================================================
    let audioCtx = null;
    let isAudioEnabled = localStorage.getItem('liqscope_audio') !== 'false';
    let alertedClusterKeys = new Set();

    // 1. Audio Engine (Web Audio API - Pure synthesized sound, zero external dependencies)
    function initAudio() {
      if (!audioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (AudioContextClass) audioCtx = new AudioContextClass();
      }
      if (audioCtx && audioCtx.state === 'suspended') {
        audioCtx.resume();
      }
      return audioCtx;
    }

    function toggleAudioAlerts() {
      isAudioEnabled = !isAudioEnabled;
      localStorage.setItem('liqscope_audio', isAudioEnabled ? 'true' : 'false');
      updateAudioUI();
      if (isAudioEnabled) playTestPing();
    }

    function updateAudioUI() {
      const btn = document.getElementById('btn-toggle-audio');
      const icon = document.getElementById('audio-icon');
      const label = document.getElementById('audio-label');
      if (!btn || !icon || !label) return;

      if (isAudioEnabled) {
        label.innerText = 'Sonido: ON';
        label.className = 'text-white font-bold';
        icon.innerText = 'volume_up';
        icon.className = 'material-symbols-outlined text-[16px] text-mark';
        btn.className = 'px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-mark/10 border-mark/30 text-white';
      } else {
        label.innerText = 'Sonido: MUTE';
        label.className = 'text-outline font-semibold';
        icon.innerText = 'volume_off';
        icon.className = 'material-symbols-outlined text-[16px] text-outline';
        btn.className = 'px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-surface-card border-surface-border text-outline hover:text-white';
      }
    }

    function playTestPing() {
      const ctx = initAudio();
      if (!ctx) return;
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.3);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.36);
    }

    function playSonarPing() {
      if (!isAudioEnabled) return;
      const ctx = initAudio();
      if (!ctx) return;
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(740, now);
      osc.frequency.exponentialRampToValueAtTime(370, now + 0.28);
      gain.gain.setValueAtTime(0.09, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.3);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.32);
    }

    function playCriticalAlarm() {
      if (!isAudioEnabled) return;
      const ctx = initAudio();
      if (!ctx) return;
      const now = ctx.currentTime;
      [0, 0.16].forEach(delay => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(940, now + delay);
        osc.frequency.exponentialRampToValueAtTime(800, now + delay + 0.1);
        gain.gain.setValueAtTime(0.12, now + delay);
        gain.gain.exponentialRampToValueAtTime(0.001, now + delay + 0.11);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + delay);
        osc.stop(now + delay + 0.12);
      });
    }

    // 2. Browser Push Notification Engine (HTML5 Notification API)
    function toggleBrowserNotifs() {
      if (!('Notification' in window)) {
        alert('Este navegador no tiene soporte para la API de Notificaciones.');
        return;
      }
      if (Notification.permission === 'granted') {
        alert('Las notificaciones ya están autorizadas y activas.');
        updateNotifUI();
        return;
      }
      Notification.requestPermission().then(() => {
        updateNotifUI();
        if (Notification.permission === 'granted') {
          try {
            new Notification('LiqScope — Radar Activado', {
              body: 'Recibirás avisos instantáneos cuando el precio alcance clústeres críticos de liquidación.',
              icon: '/favicon.ico'
            });
          } catch(e) {}
        }
      });
    }

    function updateNotifUI() {
      const btn = document.getElementById('btn-toggle-notifs');
      const icon = document.getElementById('notif-icon');
      const label = document.getElementById('notif-label');
      if (!btn || !icon || !label) return;

      if (!('Notification' in window)) {
        label.innerText = 'Push: No disp.';
        btn.classList.add('opacity-50');
        return;
      }

      if (Notification.permission === 'granted') {
        label.innerText = 'Push: Activo';
        label.className = 'text-long font-bold';
        icon.className = 'material-symbols-outlined text-[16px] text-long';
        btn.className = 'px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-long/10 border-long/30 text-long';
      } else if (Notification.permission === 'denied') {
        label.innerText = 'Push: Bloqueado';
        label.className = 'text-short font-bold';
        icon.className = 'material-symbols-outlined text-[16px] text-short';
        btn.className = 'px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-short/10 border-short/30 text-short';
      } else {
        label.innerText = 'Push: Activar';
        label.className = 'text-on-surface font-semibold';
        icon.className = 'material-symbols-outlined text-[16px] text-magnet';
        btn.className = 'px-3 py-1.5 rounded-lg border text-xs font-mono font-semibold flex items-center gap-1.5 transition-all cursor-pointer bg-surface-card border-surface-border text-on-surface hover:text-white';
      }
    }

    function triggerDesktopNotification(title, body, tag) {
      if (!('Notification' in window) || Notification.permission !== 'granted') return;
      try {
        new Notification(title, {
          body: body,
          tag: tag || 'liqscope-alert',
          renotify: false
        });
      } catch(e) {}
    }

    // 3. Navigation & Interaction Helpers
    function focusPriceInHeatmap(price) {
      switchTab('mapa-de-calor');
      inspectBinFromData(price);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function applyRadarFilter() {
      if (currentData) evaluateAlerts(currentData);
    }

    // 4. Alert Evaluation & Rendering Engine
    function evaluateAlerts(data) {
      if (!data || !data.bins || data.bins.length === 0) return;

      const mark = data.current_price;
      const proxSelect = document.getElementById('radar-proximity-select');
      const maxDeltaPct = proxSelect ? parseFloat(proxSelect.value) : 2.0;

      // Find global max cluster
      let maxClusterBin = data.bins[0];
      data.bins.forEach(b => {
        if (b.estimated_volume_usd > maxClusterBin.estimated_volume_usd) {
          maxClusterBin = b;
        }
      });

      const alerts = [];
      let hasCritical = false;
      let hasWarning = false;

      // Check simulated user position risk first
      const simEntry = parseFloat(document.getElementById('sim-entry-input')?.value);
      if (simEntry > 0 && mark > 0) {
        let simLiq = 0;
        if (simDirection === 'LONG') {
          simLiq = simEntry * (1.0 - (1.0 / simLeverage) + simMMR);
        } else {
          simLiq = simEntry * (1.0 + (1.0 / simLeverage) - simMMR);
        }
        const userDeltaPct = ((simLiq - mark) / mark) * 100;
        const userAbsDelta = Math.abs(userDeltaPct);

        if (userAbsDelta <= 5.0) {
          const isCritical = userAbsDelta <= 2.0;
          alerts.push({
            id: 'sim-user-risk',
            severity: isCritical ? 'CRITICAL' : 'WARNING',
            type: 'USER_POSITION_DANGER',
            title: isCritical ? '¡Alerta de Liquidación Propia en Peligro!' : 'Tu Posición Simulada se Acerca al Límite',
            price: simLiq,
            deltaPct: userDeltaPct,
            volumeUsd: 0,
            leverage: `${simLeverage}x`,
            side: simDirection,
            description: `El Mark Price ($${mark.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}) está a solo ${userAbsDelta.toFixed(2)}% de tu precio de liquidación simulado ($${simLiq.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}).`,
            tacticalTip: 'Considera aportar margen adicional (Margin Call), reducir apalancamiento o colocar Stop Loss antes de que el motor de Binance liquide la posición.',
            isNew: false
          });
          if (isCritical) hasCritical = true;
          else hasWarning = true;
        }
      }

      // Check MAX LIQ cluster proximity
      const maxDelta = mark > 0 ? (((maxClusterBin.price_mid - mark) / mark) * 100) : 0;
      const maxAbsDelta = Math.abs(maxDelta);
      const isMaxShort = maxClusterBin.short_volume_usd > maxClusterBin.long_volume_usd;

      if (maxAbsDelta <= maxDeltaPct) {
        const alertKey = `max-${maxClusterBin.price_mid}`;
        const isNew = !alertedClusterKeys.has(alertKey);
        const isCritical = maxAbsDelta <= 1.0;

        alerts.push({
          id: alertKey,
          severity: isCritical ? 'CRITICAL' : 'WARNING',
          type: 'MAX_LIQUIDATION_MAGNET',
          title: isMaxShort ? 'Muro Principal MAX LIQ (Cortos)' : 'Muro Principal MAX LIQ (Largos)',
          price: maxClusterBin.price_mid,
          deltaPct: maxDelta,
          volumeUsd: maxClusterBin.estimated_volume_usd,
          leverage: maxClusterBin.dominant_leverage ? `${maxClusterBin.dominant_leverage}x` : '50x',
          side: isMaxShort ? 'SHORT' : 'LONG',
          description: `Zona con mayor concentración nocional de todo el libro ($${(maxClusterBin.estimated_volume_usd / 1e6).toFixed(1)}M USD). Actúa como imán directo de liquidez.`,
          tacticalTip: isMaxShort
            ? 'Las compras forzadas de Stop Loss pueden detonar un Short Squeeze. Evita poner cortos manuales justo delante.'
            : 'Las ventas masivas de liquidación pueden empujar el precio a la baja rápidamente antes de encontrar soporte.',
          isNew: isNew
        });

        if (isCritical) hasCritical = true;
        else hasWarning = true;
        alertedClusterKeys.add(alertKey);
      }

      // Scan other dense bins close to Mark Price (< maxDeltaPct)
      const closeBins = data.bins
        .filter(b => b.price_mid !== maxClusterBin.price_mid)
        .map(b => ({
          bin: b,
          delta: mark > 0 ? (((b.price_mid - mark) / mark) * 100) : 0,
          absDelta: mark > 0 ? Math.abs(((b.price_mid - mark) / mark) * 100) : 0
        }))
        .filter(item => item.absDelta <= maxDeltaPct && item.bin.estimated_volume_usd >= (maxClusterBin.estimated_volume_usd * 0.25))
        .sort((a, b) => a.absDelta - b.absDelta);

      closeBins.slice(0, 3).forEach(item => {
        const b = item.bin;
        const isShort = b.short_volume_usd > b.long_volume_usd;
        const alertKey = `bin-${b.price_mid}`;
        const isNew = !alertedClusterKeys.has(alertKey);
        const isCritical = item.absDelta <= 0.8;

        alerts.push({
          id: alertKey,
          severity: isCritical ? 'CRITICAL' : 'WARNING',
          type: isShort ? 'SHORT_LIQ_PROXIMITY' : 'LONG_LIQ_PROXIMITY',
          title: isShort ? 'Clúster Denso de Liquidación Short' : 'Clúster Denso de Liquidación Long',
          price: b.price_mid,
          deltaPct: item.delta,
          volumeUsd: b.estimated_volume_usd,
          leverage: b.dominant_leverage ? `${b.dominant_leverage}x` : 'Multi',
          side: isShort ? 'SHORT' : 'LONG',
          description: `Concentración de $${(b.estimated_volume_usd / 1e6).toFixed(1)}M USD a solo ${item.absDelta.toFixed(2)}% del precio actual.`,
          tacticalTip: isShort
            ? 'Barrido de cortos próximo. Los traders atrapados tendrán que comprar a mercado para cerrar.'
            : 'Barrido de largos próximo. Oportunidad para buscar absorción (Sweep & Reverse) una vez limpiado el nivel.',
          isNew: isNew
        });

        if (isCritical) hasCritical = true;
        else hasWarning = true;
        alertedClusterKeys.add(alertKey);
      });

      // Scan for Domino Cascade Risk (3 consecutive bins close together with high volume)
      const shortsNear = data.bins.filter(b => b.price_mid > mark && (((b.price_mid - mark) / mark) * 100) <= 2.2);
      const longsNear = data.bins.filter(b => b.price_mid < mark && (((mark - b.price_mid) / mark) * 100) <= 2.2);

      if (shortsNear.length >= 3) {
        const cascadeVol = shortsNear.reduce((acc, x) => acc + x.estimated_volume_usd, 0);
        if (cascadeVol >= 80e6) {
          alerts.push({
            id: 'cascade-shorts',
            severity: 'WARNING',
            type: 'CASCADE_RISK_SHORT',
            title: 'Riesgo de Cascada de Liquidación Alcista',
            price: shortsNear[0].price_mid,
            deltaPct: ((shortsNear[0].price_mid - mark) / mark) * 100,
            volumeUsd: cascadeVol,
            leverage: '100x/50x',
            side: 'SHORT',
            description: `Se detectan ${shortsNear.length} niveles contiguos de cortos acumulando $${(cascadeVol / 1e6).toFixed(1)}M USD a menos del 2.2% del Mark.`,
            tacticalTip: 'Si el precio penetra el primer clúster, las compras forzadas consecutivas pueden provocar un salto repentino de precio.',
            isNew: false
          });
          hasWarning = true;
        }
      }

      if (longsNear.length >= 3) {
        const cascadeVol = longsNear.reduce((acc, x) => acc + x.estimated_volume_usd, 0);
        if (cascadeVol >= 80e6) {
          alerts.push({
            id: 'cascade-longs',
            severity: 'WARNING',
            type: 'CASCADE_RISK_LONG',
            title: 'Riesgo de Cascada de Liquidación Bajista',
            price: longsNear[0].price_mid,
            deltaPct: ((longsNear[0].price_mid - mark) / mark) * 100,
            volumeUsd: cascadeVol,
            leverage: '100x/50x',
            side: 'LONG',
            description: `Se detectan ${longsNear.length} niveles contiguos de largos acumulando $${(cascadeVol / 1e6).toFixed(1)}M USD a menos del 2.2% del Mark.`,
            tacticalTip: 'Peligro de liquidaciones en cadena a la baja. No colocar órdenes límite de compra antes de confirmar absorción en el volumen.',
            isNew: false
          });
          hasWarning = true;
        }
      }

      // Check Extreme L/S Account Ratio Asymmetry
      if (data.long_account_ratio >= 0.60) {
        alerts.push({
          id: 'skew-long',
          severity: 'INFO',
          type: 'ASYMMETRY_SKEW',
          title: 'Desbalance Extremo de Cuentas (Mayoría Long)',
          price: mark,
          deltaPct: 0,
          volumeUsd: data.total_open_interest_usd,
          leverage: 'Market',
          side: 'LONG',
          description: `El ${(data.long_account_ratio * 100).toFixed(1)}% de las cuentas en Binance están posicionadas en largo.`,
          tacticalTip: 'El mercado minorista está sobre-posicionado al alza. Típicamente los creadores de mercado inducen caídas para barrer el lado mayoritario.',
          isNew: false
        });
      } else if (data.short_account_ratio >= 0.60) {
        alerts.push({
          id: 'skew-short',
          severity: 'INFO',
          type: 'ASYMMETRY_SKEW',
          title: 'Desbalance Extremo de Cuentas (Mayoría Short)',
          price: mark,
          deltaPct: 0,
          volumeUsd: data.total_open_interest_usd,
          leverage: 'Market',
          side: 'SHORT',
          description: `El ${(data.short_account_ratio * 100).toFixed(1)}% de las cuentas en Binance están posicionadas en corto.`,
          tacticalTip: 'El sentimiento minorista es excesivamente pesimista. Elevada probabilidad de Short Squeeze buscando liquidar a vendedores tardíos.',
          isNew: false
        });
      }

      // Render alerts to DOM
      renderAlertsList(alerts, mark);

      // Trigger Audio and Desktop Notifications
      if (hasCritical) {
        playCriticalAlarm();
        const criticalAlert = alerts.find(a => a.severity === 'CRITICAL');
        if (criticalAlert) {
          triggerDesktopNotification(
            `🚨 LiqScope: ${criticalAlert.title}`,
            `${currentSymbol} a $${criticalAlert.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} (${criticalAlert.deltaPct >= 0 ? '+' : ''}${criticalAlert.deltaPct.toFixed(2)}%). Volumen: $${(criticalAlert.volumeUsd / 1e6).toFixed(1)}M`,
            criticalAlert.id
          );
          dispatchTelegramAlert(criticalAlert);
        }
      } else if (hasWarning) {
        playSonarPing();
      }
    }

    // 5. Render Alerts Stream to DOM
    function renderAlertsList(alerts, mark) {
      const container = document.getElementById('alerts-stream');
      const countCritEl = document.getElementById('count-critical');
      const countWarnEl = document.getElementById('count-warning');
      const countInfoEl = document.getElementById('count-info');
      const topBadge = document.getElementById('top-alert-badge');
      const mobileBadge = document.getElementById('mobile-alert-badge');

      if (!container) return;

      const critCount = alerts.filter(a => a.severity === 'CRITICAL').length;
      const warnCount = alerts.filter(a => a.severity === 'WARNING').length;
      const infoCount = alerts.filter(a => a.severity === 'INFO').length;

      if (countCritEl) countCritEl.innerText = critCount;
      if (countWarnEl) countWarnEl.innerText = warnCount;
      if (countInfoEl) countInfoEl.innerText = infoCount;

      const totalImportant = critCount + warnCount;
      if (topBadge) {
        if (totalImportant > 0) {
          topBadge.innerText = totalImportant;
          topBadge.classList.remove('hidden');
        } else {
          topBadge.classList.add('hidden');
        }
      }
      if (mobileBadge) {
        if (totalImportant > 0) {
          mobileBadge.innerText = totalImportant;
          mobileBadge.classList.remove('hidden');
        } else {
          mobileBadge.classList.add('hidden');
        }
      }

      if (alerts.length === 0) {
        container.innerHTML = `
          <div class="bg-surface-panel border border-surface-border rounded-xl p-8 text-center flex flex-col items-center justify-center gap-2">
            <span class="material-symbols-outlined text-[36px] text-long">verified</span>
            <span class="font-mono text-sm font-bold text-white">Zona de Baja Densidad de Liquidación</span>
            <p class="font-mono text-xs text-outline max-w-md">No se detectan clústeres críticos en el rango inmediato. El precio se mueve sin fricción extrema de liquidaciones forzadas.</p>
          </div>
        `;
        return;
      }

      let html = '';
      alerts.forEach(a => {
        let borderColor = 'border-surface-border';
        let leftBarColor = 'bg-mark';
        let badgeColor = 'bg-mark/15 text-mark border-mark/30';
        let badgeText = 'INFO';

        if (a.severity === 'CRITICAL') {
          borderColor = 'border-short/50 shadow-lg shadow-short/10';
          leftBarColor = a.side === 'SHORT' ? 'bg-short' : (a.side === 'LONG' ? 'bg-long' : 'bg-magnet');
          badgeColor = 'bg-short/20 text-short border-short/40 animate-pulse';
          badgeText = 'CRÍTICA';
        } else if (a.severity === 'WARNING') {
          borderColor = 'border-magnet/40';
          leftBarColor = 'bg-magnet';
          badgeColor = 'bg-magnet/20 text-magnet border-magnet/40';
          badgeText = 'ATENCIÓN';
        } else {
          leftBarColor = 'bg-mark';
          badgeColor = 'bg-mark/15 text-mark border-mark/30';
          badgeText = 'SENTIMIENTO';
        }

        const deltaFormatted = `${a.deltaPct >= 0 ? '+' : ''}${a.deltaPct.toFixed(2)}%`;
        const volFormatted = a.volumeUsd > 0 ? `$${(a.volumeUsd / 1e6).toFixed(1)}M USD` : 'Posición simulada';

        html += `
          <div class="bg-surface-panel border ${borderColor} rounded-xl p-3.5 relative overflow-hidden flex flex-col gap-2 transition-all hover:bg-surface-card">
            <!-- Left accent stripe -->
            <div class="absolute left-0 top-0 bottom-0 w-1.5 ${leftBarColor}"></div>

            <!-- Card Header: Badge, Title & Delta Price -->
            <div class="flex items-center justify-between pl-2 flex-wrap gap-2">
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[9px] font-mono font-black uppercase border ${badgeColor}">${badgeText}</span>
                <span class="font-mono text-xs font-bold text-white tracking-wide">${a.title}</span>
              </div>
              <div class="flex items-center gap-1.5 font-mono text-xs font-bold">
                <span class="text-white">$${a.price.toLocaleString('en-US', { minimumFractionDigits: currentSymbol === 'ETHUSDT' ? 2 : 0, maximumFractionDigits: 2 })}</span>
                <span class="px-1.5 py-0.2 rounded bg-surface border border-surface-border text-[10px] ${a.deltaPct >= 0 ? 'text-short' : 'text-long'}">${deltaFormatted}</span>
              </div>
            </div>

            <!-- Card Body: Metrics & Description -->
            <div class="pl-2 flex flex-col gap-1.5">
              <p class="text-xs text-on-surface-variant font-mono leading-relaxed">
                ${a.description}
              </p>

              <!-- Tags row: Volume, Leverage & Symbol -->
              <div class="flex items-center gap-2 flex-wrap text-[10px] font-mono pt-0.5">
                <span class="px-2 py-0.5 rounded bg-surface border border-surface-border text-white font-bold flex items-center gap-1">
                  <span class="text-outline">Vol:</span> ${volFormatted}
                </span>
                <span class="px-2 py-0.5 rounded bg-surface border border-surface-border text-white font-bold flex items-center gap-1">
                  <span class="text-outline">Palanca:</span> ${a.leverage}
                </span>
                <span class="px-2 py-0.5 rounded bg-surface border border-surface-border text-mark font-bold">${currentSymbol}</span>
              </div>

              <!-- Tactical Tip Box -->
              <div class="mt-1 p-2 rounded-lg bg-surface/80 border border-surface-border-subtle flex items-start gap-2 text-[11px] font-mono text-on-surface">
                <span class="material-symbols-outlined text-[15px] text-magnet shrink-0 mt-0.5">lightbulb</span>
                <span class="leading-relaxed"><strong class="text-white">Acción Táctica:</strong> ${a.tacticalTip}</span>
              </div>
            </div>

            <!-- Card Action Footer -->
            <div class="pl-2 pt-1 flex items-center justify-between border-t border-surface-border/50 text-xs font-mono">
              <span class="text-[10px] text-outline">Telemetría Binance Live Sync</span>
              <div class="flex items-center gap-2">
                <button onclick="sendSingleAlertToTelegram('${a.title}', ${a.price}, ${a.deltaPct}, ${a.volumeUsd}, '${a.leverage}', '${a.side || 'SHORT'}', '${(a.tacticalTip || '').replace(/'/g, "\\'")}')" class="px-2 py-1 rounded bg-[#2AABEE]/10 hover:bg-[#2AABEE]/20 text-[#2AABEE] border border-[#2AABEE]/30 text-[11px] font-bold flex items-center gap-1 transition-all cursor-pointer" title="Enviar esta alerta ahora a Telegram">
                  <span class="material-symbols-outlined text-[13px]">send</span>
                  <span class="hidden xs:inline">Telegram</span>
                </button>
                <button onclick="focusPriceInHeatmap(${a.price})" class="px-2.5 py-1 rounded bg-surface-card hover:bg-mark/10 text-mark border border-mark/25 text-[11px] font-bold flex items-center gap-1 transition-all cursor-pointer">
                  <span class="material-symbols-outlined text-[14px]">visibility</span>
                  <span>Ver en Heatmap</span>
                </button>
              </div>
            </div>
          </div>
        `;
      });

      container.innerHTML = html;
    }

    // ==========================================
    // TELEGRAM BOT ALERT ENGINE & HANDLERS
    // ==========================================
    let tgBotToken = localStorage.getItem('liqscope_tg_token') || '8029722060:AAEwmNd0OVZ3z9uQRMHFdgkpX9wwjNx6u28';
    let tgChatId = localStorage.getItem('liqscope_tg_chat') || '1068166949';
    let tgAutoDispatch = localStorage.getItem('liqscope_tg_auto') !== 'false';
    let tgSentAlertKeys = new Set();

    function initTelegramUI() {
      if (!localStorage.getItem('liqscope_tg_token')) {
        localStorage.setItem('liqscope_tg_token', tgBotToken);
      }
      if (!localStorage.getItem('liqscope_tg_chat')) {
        localStorage.setItem('liqscope_tg_chat', tgChatId);
      }
      const tokenInput = document.getElementById('tg-token-input');
      const chatInput = document.getElementById('tg-chat-input');
      const autoCheck = document.getElementById('tg-auto-dispatch-check');
      if (tokenInput) tokenInput.value = tgBotToken;
      if (chatInput) chatInput.value = tgChatId;
      if (autoCheck) autoCheck.checked = tgAutoDispatch;
      updateTgStatusPill();
    }

    async function autoDetectTelegramChat() {
      const token = document.getElementById('tg-token-input').value.trim() || tgBotToken;
      if (!token) {
        showTgFeedback(false, 'Introduce el Bot Token primero.');
        return;
      }

      showTgFeedback(true, 'Buscando tu mensaje en @criptobtctrader_bot...', true);
      try {
        const resp = await fetch('/api/v1/alerts/telegram/detect-chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ bot_token: token })
        });
        const res = await resp.json();
        if (res.success && res.chat_id) {
          document.getElementById('tg-chat-input').value = res.chat_id;
          tgChatId = res.chat_id;
          localStorage.setItem('liqscope_tg_chat', tgChatId);
          updateTgStatusPill();
          showTgFeedback(true, `✓ Chat ID detectado: ${res.chat_id} (${res.message}). ¡Ahora pulsa Probar Conexión!`);
        } else {
          showTgFeedback(false, res.message || 'No se encontró mensaje. Pulsa Iniciar en @criptobtctrader_bot y vuelve a intentarlo.');
        }
      } catch(e) {
        showTgFeedback(false, 'Error de red al detectar el chat.');
      }
    }

    function toggleTgPanel() {
      const body = document.getElementById('tg-config-body');
      const chevron = document.getElementById('tg-chevron');
      const toggleText = document.getElementById('tg-panel-toggle-text');
      if (!body) return;
      const isHidden = body.classList.contains('hidden');
      if (isHidden) {
        body.classList.remove('hidden');
        if (chevron) chevron.innerText = 'expand_less';
        if (toggleText) toggleText.innerText = 'Cerrar';
      } else {
        body.classList.add('hidden');
        if (chevron) chevron.innerText = 'expand_more';
        if (toggleText) toggleText.innerText = 'Configurar';
      }
    }

    function toggleTokenVisibility() {
      const input = document.getElementById('tg-token-input');
      const icon = document.getElementById('token-vis-icon');
      if (!input || !icon) return;
      if (input.type === 'password') {
        input.type = 'text';
        icon.innerText = 'visibility_off';
      } else {
        input.type = 'password';
        icon.innerText = 'visibility';
      }
    }

    function updateTgStatusPill() {
      const pill = document.getElementById('tg-status-pill');
      if (!pill) return;
      if (tgBotToken && tgChatId) {
        if (tgAutoDispatch) {
          pill.innerText = 'CONECTADO & ACTIVO';
          pill.className = 'px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-long/15 text-long border border-long/30';
        } else {
          pill.innerText = 'CONECTADO (MANUAL)';
          pill.className = 'px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-[#2AABEE]/15 text-[#2AABEE] border border-[#2AABEE]/30';
        }
      } else {
        pill.innerText = 'DESCONECTADO';
        pill.className = 'px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-surface border border-surface-border text-outline';
      }
    }

    function saveTelegramSettings() {
      const tokenInput = document.getElementById('tg-token-input');
      const chatInput = document.getElementById('tg-chat-input');
      if (tokenInput) tgBotToken = tokenInput.value.trim();
      if (chatInput) tgChatId = chatInput.value.trim();

      localStorage.setItem('liqscope_tg_token', tgBotToken);
      localStorage.setItem('liqscope_tg_chat', tgChatId);
      updateTgStatusPill();
      showTgFeedback(true, 'Configuración de Telegram guardada correctamente.');
    }

    function toggleTgAutoDispatch() {
      const autoCheck = document.getElementById('tg-auto-dispatch-check');
      tgAutoDispatch = autoCheck ? autoCheck.checked : false;
      localStorage.setItem('liqscope_tg_auto', tgAutoDispatch ? 'true' : 'false');
      updateTgStatusPill();
    }

    async function testTelegramConnection() {
      saveTelegramSettings();
      if (!tgBotToken || !tgChatId) {
        showTgFeedback(false, 'Por favor ingresa tanto el Bot Token como el Chat ID.');
        return;
      }

      const btn = document.getElementById('btn-tg-test');
      if (btn) btn.disabled = true;
      showTgFeedback(true, 'Enviando mensaje de prueba a Telegram...', true);

      try {
        const resp = await fetch('/api/v1/alerts/telegram/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ bot_token: tgBotToken, chat_id: tgChatId })
        });
        const result = await resp.json();
        if (resp.ok && result.success) {
          showTgFeedback(true, '✓ ¡Mensaje de prueba recibido en tu Telegram!');
          updateTgStatusPill();
        } else {
          showTgFeedback(false, result.detail || result.message || 'Error al conectar con Telegram.');
        }
      } catch (err) {
        showTgFeedback(false, 'Error de red al conectar con la API local de LiqScope.');
      } finally {
        if (btn) btn.disabled = false;
      }
    }

    function showTgFeedback(isSuccess, message, isLoading = false) {
      const box = document.getElementById('tg-feedback-msg');
      if (!box) return;
      box.classList.remove('hidden');
      if (isLoading) {
        box.className = 'p-2.5 rounded-lg text-xs font-mono flex items-center gap-2 bg-mark/10 text-mark border border-mark/30';
        box.innerHTML = `<span class="material-symbols-outlined text-[16px] animate-spin">progress_activity</span><span>${message}</span>`;
      } else if (isSuccess) {
        box.className = 'p-2.5 rounded-lg text-xs font-mono flex items-center gap-2 bg-long/10 text-long border border-long/30';
        box.innerHTML = `<span class="material-symbols-outlined text-[16px]">check_circle</span><span>${message}</span>`;
      } else {
        box.className = 'p-2.5 rounded-lg text-xs font-mono flex items-center gap-2 bg-short/10 text-short border border-short/30';
        box.innerHTML = `<span class="material-symbols-outlined text-[16px]">error</span><span>${message}</span>`;
      }
    }

    async function dispatchTelegramAlert(alertObj) {
      if (!tgAutoDispatch || !tgBotToken || !tgChatId) return;
      const key = `${currentSymbol}-${alertObj.id}`;
      if (tgSentAlertKeys.has(key)) return;

      try {
        const resp = await fetch('/api/v1/alerts/telegram/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bot_token: tgBotToken,
            chat_id: tgChatId,
            title: alertObj.title,
            symbol: currentSymbol,
            price: alertObj.price,
            delta_pct: alertObj.deltaPct,
            volume_usd: alertObj.volumeUsd,
            leverage: alertObj.leverage,
            side: alertObj.side || 'SHORT',
            tactical_tip: alertObj.tacticalTip || ''
          })
        });
        if (resp.ok) {
          tgSentAlertKeys.add(key);
        }
      } catch (e) {
        console.warn('Telegram automated dispatch failed:', e);
      }
    }

    async function sendSingleAlertToTelegram(title, price, deltaPct, volUsd, lev, side, tip) {
      if (!tgBotToken || !tgChatId) {
        toggleTgPanel();
        showTgFeedback(false, 'Por favor, configura y guarda tu Bot Token y Chat ID primero.');
        return;
      }
      try {
        const resp = await fetch('/api/v1/alerts/telegram/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            bot_token: tgBotToken,
            chat_id: tgChatId,
            title: title,
            symbol: currentSymbol,
            price: price,
            delta_pct: deltaPct,
            volume_usd: volUsd,
            leverage: lev,
            side: side,
            tactical_tip: tip
          })
        });
        const res = await resp.json();
        if (resp.ok && res.success) {
          alert('✓ ¡Alerta enviada exitosamente a tu Telegram!');
        } else {
          alert(`Error al enviar a Telegram: ${res.detail || res.message}`);
        }
      } catch (e) {
        alert('Error de red al comunicar con el servidor.');
      }
    }

    // ==========================================
    // REKT TICKER & LIVE WEBSOCKET AUDIO ENGINE
    // ==========================================
    let rektAudioEnabled = localStorage.getItem('liqscope_rekt_audio') !== 'false';
    let rektAudioThreshold = parseFloat(localStorage.getItem('liqscope_rekt_threshold') || '100000');
    let rektEvents = [];
    let rektStats = {
      total_count: 0,
      total_volume_usd: 0,
      long_count: 0,
      long_volume_usd: 0,
      short_count: 0,
      short_volume_usd: 0,
      whale_count: 0,
      largest_event: null
    };
    let rektSocket = null;
    let rektAudioCtx = null;

    function getRektAudioContext() {
      if (!rektAudioCtx) {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          rektAudioCtx = new AudioCtx();
        }
      }
      if (rektAudioCtx && rektAudioCtx.state === 'suspended') {
        rektAudioCtx.resume();
      }
      return rektAudioCtx;
    }

    function initRektAudioUI() {
      const toggleBtn = document.getElementById('rekt-audio-toggle');
      const toggleText = document.getElementById('rekt-audio-text');
      const toggleIcon = document.getElementById('rekt-audio-icon');
      const selThreshold = document.getElementById('rekt-audio-threshold');

      if (selThreshold) {
        selThreshold.value = rektAudioThreshold.toString();
      }

      if (toggleBtn && toggleText && toggleIcon) {
        if (rektAudioEnabled) {
          toggleBtn.className = 'px-3 py-1.5 rounded-lg bg-mark/15 border border-mark/40 text-mark font-mono text-xs font-bold flex items-center gap-1.5 transition-all cursor-pointer shadow-xs';
          toggleIcon.innerText = 'volume_up';
          toggleText.innerText = 'Audio: ON';
        } else {
          toggleBtn.className = 'px-3 py-1.5 rounded-lg bg-surface border border-surface-border text-outline hover:text-white font-mono text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer';
          toggleIcon.innerText = 'volume_off';
          toggleText.innerText = 'Audio: MUTE';
        }
      }
    }

    function toggleRektAudio() {
      rektAudioEnabled = !rektAudioEnabled;
      localStorage.setItem('liqscope_rekt_audio', rektAudioEnabled ? 'true' : 'false');
      initRektAudioUI();
      if (rektAudioEnabled) {
        getRektAudioContext();
        playRektAudio(120000, 'LONG'); // Preview chime
      }
    }

    function setRektAudioThreshold(val) {
      rektAudioThreshold = parseFloat(val);
      localStorage.setItem('liqscope_rekt_threshold', val);
    }

    function playRektAudio(volumeUsd, side) {
      if (!rektAudioEnabled) return;
      if (volumeUsd < rektAudioThreshold) return;

      const ctx = getRektAudioContext();
      if (!ctx) return;

      const now = ctx.currentTime;

      if (volumeUsd >= 500000) {
        // MEGA WHALE (> $500K): Deep sub-bass cinematic slam
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(100, now);
        osc.frequency.exponentialRampToValueAtTime(24, now + 0.65);

        gain.gain.setValueAtTime(0.4, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.75);
      } else if (volumeUsd >= 100000) {
        // WHALE (> $100K): Punchy low-frequency thud
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(140, now);
        osc.frequency.exponentialRampToValueAtTime(36, now + 0.38);

        gain.gain.setValueAtTime(0.35, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.42);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.45);
      } else {
        // Standard Liquidation: Tech chime
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        const startFreq = side === 'LONG' ? 520 : 760;
        const endFreq = side === 'LONG' ? 380 : 920;
        osc.frequency.setValueAtTime(startFreq, now);
        osc.frequency.exponentialRampToValueAtTime(endFreq, now + 0.12);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.16);
      }
    }

    function initRektWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/liquidations`;

      try {
        rektSocket = new WebSocket(wsUrl);

        rektSocket.onopen = () => {
          updateRektWsBadge(true);
        };

        rektSocket.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data);
            if (msg.type === 'liquidation' && msg.data) {
              handleIncomingLiquidation(msg.data);
            } else if (msg.type === 'connected' && msg.stats) {
              updateRektStatsUI(msg.stats);
            }
          } catch (e) {
            console.warn('REKT WS message error:', e);
          }
        };

        rektSocket.onclose = () => {
          updateRektWsBadge(false);
          setTimeout(initRektWebSocket, 3500);
        };

        rektSocket.onerror = () => {
          updateRektWsBadge(false);
        };
      } catch (err) {
        console.warn('REKT WS connection error:', err);
        setTimeout(initRektWebSocket, 5000);
      }
    }

    function updateRektWsBadge(connected) {
      const badge = document.getElementById('rekt-ws-badge');
      const text = document.getElementById('rekt-ws-status-text');
      if (badge && text) {
        if (connected) {
          badge.className = 'px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold border border-emerald-500/30 flex items-center gap-1.5';
          text.innerText = 'WS EN VIVO (BINANCE)';
        } else {
          badge.className = 'px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-mono text-[10px] font-bold border border-amber-500/30 flex items-center gap-1.5';
          text.innerText = 'RECONECTANDO...';
        }
      }
    }

    function handleIncomingLiquidation(ev) {
      if (!ev) return;

      // Add to memory list
      rektEvents.unshift(ev);
      if (rektEvents.length > 200) rektEvents.pop();

      // Update Session Stats
      rektStats.total_count += 1;
      rektStats.total_volume_usd += ev.volume_usd;
      if (ev.liquidated_side === 'LONG') {
        rektStats.long_count += 1;
        rektStats.long_volume_usd += ev.volume_usd;
      } else {
        rektStats.short_count += 1;
        rektStats.short_volume_usd += ev.volume_usd;
      }
      if (ev.is_whale) rektStats.whale_count += 1;
      if (!rektStats.largest_event || ev.volume_usd > rektStats.largest_event.volume_usd) {
        rektStats.largest_event = ev;
      }

      updateRektStatsUI(rektStats);
      updateRektTape(ev);
      renderRektTable();
      playRektAudio(ev.volume_usd, ev.liquidated_side);
    }

    function updateRektTape(ev) {
      const container = document.getElementById('rekt-tape-container');
      if (!container) return;

      const isLong = ev.liquidated_side === 'LONG';
      const color = isLong ? 'text-short' : 'text-long';
      const icon = isLong ? 'trending_down' : 'trending_up';
      const whaleTag = ev.is_mega_whale ? ' 🐋 MEGA' : (ev.is_whale ? ' 🐳' : '');
      const volFormatted = ev.volume_usd >= 1e6
        ? `$${(ev.volume_usd / 1e6).toFixed(2)}M`
        : `$${(ev.volume_usd / 1e3).toFixed(1)}K`;

      const itemHtml = `
        <span class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-surface border border-surface-border animate-fade-in shrink-0">
          <span class="material-symbols-outlined text-[13px] ${color}">${icon}</span>
          <strong class="text-white">${ev.symbol}</strong>
          <span class="${color} font-bold">${ev.liquidated_side}</span>
          <span class="text-white font-extrabold">${volFormatted}${whaleTag}</span>
          <span class="text-outline text-[10px]">@ $${ev.avg_price.toLocaleString('en-US', { maximumFractionDigits: 4 })}</span>
        </span>
      `;

      // Keep up to 5 items in the ribbon
      if (container.children.length === 0 || container.innerText.includes('Conectando')) {
        container.innerHTML = itemHtml;
      } else {
        container.insertAdjacentHTML('afterbegin', itemHtml);
        while (container.children.length > 5) {
          container.removeChild(container.lastChild);
        }
      }
    }

    function updateRektStatsUI(stats) {
      if (!stats) return;

      const totalUsdEl = document.getElementById('rekt-stat-total-usd');
      const totalCountEl = document.getElementById('rekt-stat-total-count');
      const longUsdEl = document.getElementById('rekt-stat-long-usd');
      const longRatioEl = document.getElementById('rekt-stat-long-ratio');
      const shortUsdEl = document.getElementById('rekt-stat-short-usd');
      const shortRatioEl = document.getElementById('rekt-stat-short-ratio');
      const whaleCountEl = document.getElementById('rekt-stat-whale-count');
      const largestEl = document.getElementById('rekt-stat-largest');

      const fmtM = (v) => v >= 1e6 ? `$${(v / 1e6).toFixed(2)}M` : `$${(v / 1e3).toFixed(1)}K`;

      if (totalUsdEl) totalUsdEl.innerText = fmtM(stats.total_volume_usd);
      if (totalCountEl) totalCountEl.innerText = `${stats.total_count.toLocaleString()} liquidaciones`;

      const totalVol = Math.max(stats.total_volume_usd, 1);
      const longPct = ((stats.long_volume_usd / totalVol) * 100).toFixed(1);
      const shortPct = ((stats.short_volume_usd / totalVol) * 100).toFixed(1);

      if (longUsdEl) longUsdEl.innerText = fmtM(stats.long_volume_usd);
      if (longRatioEl) longRatioEl.innerText = `${stats.long_count} órdenes (${longPct}%)`;

      if (shortUsdEl) shortUsdEl.innerText = fmtM(stats.short_volume_usd);
      if (shortRatioEl) shortRatioEl.innerText = `${stats.short_count} órdenes (${shortPct}%)`;

      if (whaleCountEl) whaleCountEl.innerText = stats.whale_count;

      if (largestEl && stats.largest_event) {
        const le = stats.largest_event;
        const leVol = fmtM(le.volume_usd);
        largestEl.innerHTML = `<span class="text-white font-bold">${le.symbol}</span> ${le.liquidated_side}: <span class="text-mark font-bold">${leVol}</span>`;
      }
    }

    function filterRektFeed() {
      const symSelect = document.getElementById('rekt-filter-symbol');
      const sizeSelect = document.getElementById('rekt-filter-min-size');

      rektFilterSymbol = symSelect ? symSelect.value : 'ALL';
      rektFilterMinSize = sizeSelect ? parseFloat(sizeSelect.value) : 0;

      renderRektTable();
    }

    function renderRektTable() {
      const tbody = document.getElementById('rekt-table-body');
      const countBadge = document.getElementById('rekt-count-badge');
      if (!tbody) return;

      const filtered = rektEvents.filter(ev => {
        if (rektFilterSymbol === 'BTCUSDT' && ev.symbol !== 'BTCUSDT') return false;
        if (rektFilterSymbol === 'ETHUSDT' && ev.symbol !== 'ETHUSDT') return false;
        if (rektFilterSymbol === 'ALTS' && (ev.symbol === 'BTCUSDT' || ev.symbol === 'ETHUSDT')) return false;
        if (ev.volume_usd < rektFilterMinSize) return false;
        return true;
      });

      if (countBadge) {
        countBadge.innerText = `${filtered.length} eventos`;
      }

      if (filtered.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="7" class="py-8 text-center text-outline font-mono text-xs">
              Sin liquidaciones que coincidan con los filtros seleccionados.
            </td>
          </tr>
        `;
        return;
      }

      let html = '';
      filtered.slice(0, 80).forEach(ev => {
        const isLong = ev.liquidated_side === 'LONG';
        const sideClass = isLong
          ? 'bg-short/15 text-short border-short/30'
          : 'bg-long/15 text-long border-long/30';
        const sideIcon = isLong ? 'trending_down' : 'trending_up';
        const timeStr = new Date(ev.timestamp).toLocaleTimeString();

        let badgeWhale = '';
        if (ev.is_mega_whale) {
          badgeWhale = `<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/40 text-[10px] font-bold">🐋 MEGA WHALE</span>`;
        } else if (ev.is_whale) {
          badgeWhale = `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold">🐳 BALLENA</span>`;
        } else if (ev.volume_usd >= 25000) {
          badgeWhale = `<span class="px-2 py-0.5 rounded bg-surface-card text-white border border-surface-border text-[10px] font-semibold">TIBURÓN</span>`;
        } else {
          badgeWhale = `<span class="px-2 py-0.5 rounded bg-surface text-outline text-[10px]">MINORISTA</span>`;
        }

        const volFmt = `$${ev.volume_usd.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
        const priceFmt = `$${ev.avg_price.toLocaleString('en-US', { maximumFractionDigits: ev.avg_price < 1 ? 5 : 2 })}`;

        html += `
          <tr class="hover:bg-surface-card/60 transition-colors">
            <td class="py-2.5 px-3 text-outline text-[11px]">${timeStr}</td>
            <td class="py-2.5 px-3 font-bold text-white flex items-center gap-1.5">
              <span>${ev.symbol}</span>
            </td>
            <td class="py-2.5 px-3">
              <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded border text-[11px] font-bold ${sideClass}">
                <span class="material-symbols-outlined text-[13px]">${sideIcon}</span>
                <span>${ev.liquidated_side} REKT</span>
              </span>
            </td>
            <td class="py-2.5 px-3 text-right font-bold text-white">${priceFmt}</td>
            <td class="py-2.5 px-3 text-right text-outline">${ev.quantity.toLocaleString('en-US', { maximumFractionDigits: 4 })}</td>
            <td class="py-2.5 px-3 text-right font-black ${isLong ? 'text-short' : 'text-long'}">${volFmt}</td>
            <td class="py-2.5 px-3 text-center">${badgeWhale}</td>
          </tr>
        `;
      });

      tbody.innerHTML = html;
    }

    function clearRektTable() {
      rektEvents = [];
      renderRektTable();
      const container = document.getElementById('rekt-tape-container');
      if (container) {
        container.innerHTML = '<span class="text-outline text-xs animate-pulse">Esperando nuevas liquidaciones en tiempo real...</span>';
      }
    }

    async function fetchRecentLiquidations() {
      try {
        const resp = await fetch('/api/v1/liquidations/recent?limit=60');
        if (resp.ok) {
          const data = await resp.json();
          if (data.events && data.events.length > 0) {
            const existingIds = new Set(rektEvents.map(e => `${e.symbol}-${e.timestamp}-${e.volume_usd}`));
            data.events.forEach(ev => {
              const id = `${ev.symbol}-${ev.timestamp}-${ev.volume_usd}`;
              if (!existingIds.has(id)) {
                rektEvents.push(ev);
                existingIds.add(id);
              }
            });
            rektEvents.sort((a, b) => b.timestamp - a.timestamp);
            if (data.stats) {
              rektStats = data.stats;
              updateRektStatsUI(rektStats);
            }
            renderRektTable();
            if (rektEvents.length > 0) {
              updateRektTape(rektEvents[0]);
            }
          }
        }
      } catch (err) {
        console.warn('Fallo al obtener liquidaciones recientes:', err);
      }
    }

    // ==============================================================
    // TRADINGVIEW + LIQSCOPE LIQUIDATION HEATMAP RENDERING ENGINE
    // ==============================================================
    let tvChart = null;
    let tvCandleSeries = null;
    let tvVolumeSeries = null;
    let tvTimeframe = '1h';
    let tvOverlaysEnabled = true;
    let tvActivePriceLines = [];
    let tvKlinesData = [];
    let tvPalette = 'liqscope';
    let tvIntensityMultiplier = 1.5;
    let tvHeatmapRenderPending = false;

    // Súper Gráficos Sub-panels (Open Interest & Funding History)
    let tvSubOiEnabled = false;
    let tvSubFundingEnabled = false;
    let tvOiChart = null;
    let tvOiSeries = null;
    let tvOiData = [];
    let tvFundingChart = null;
    let tvFundingHistSeries = null;
    let tvFundingData = [];
    let isSyncingSubRanges = false;

    function syncCanvasSize() {
      const container = document.getElementById('tv-chart-canvas');
      const canvas = document.getElementById('tv-heatmap-canvas');
      if (!container || !canvas) return;

      const dpr = window.devicePixelRatio || 1;
      const w = container.clientWidth;
      const h = container.clientHeight;

      if (w <= 0 || h <= 0) return;

      const targetW = Math.round(w * dpr);
      const targetH = Math.round(h * dpr);

      if (canvas.width !== targetW || canvas.height !== targetH) {
        canvas.width = targetW;
        canvas.height = targetH;
        canvas.style.width = `${w}px`;
        canvas.style.height = `${h}px`;
      }
    }

    function requestRenderTvHeatmap() {
      if (tvHeatmapRenderPending) return;
      tvHeatmapRenderPending = true;
      requestAnimationFrame(() => {
        tvHeatmapRenderPending = false;
        renderTvHeatmap();
      });
    }

    function changeTvPalette(val) {
      tvPalette = val;
      updateLegendGradientBar(val);
      requestRenderTvHeatmap();
    }

    function changeTvIntensity(val) {
      tvIntensityMultiplier = parseFloat(val) || 1.5;
      requestRenderTvHeatmap();
    }

    function updateLegendGradientBar(palette) {
      const bar = document.getElementById('tv-legend-gradient-bar');
      if (!bar) return;
      if (palette === 'longshort') {
        bar.className = 'w-24 h-2 rounded-sm bg-gradient-to-r from-[#ff3358] via-[#ffd700] to-[#00f090]';
      } else if (palette === 'plasma') {
        bar.className = 'w-24 h-2 rounded-sm bg-gradient-to-r from-[#330066] via-[#cc0099] via-[#00e5ff] to-[#ffffff]';
      } else {
        bar.className = 'w-24 h-2 rounded-sm bg-gradient-to-r from-[#181f5c] via-[#00bfff] via-[#50f05a] to-[#ffff00]';
      }
    }

    function resetTvChartZoom() {
      if (tvChart) {
        tvChart.timeScale().fitContent();
        requestRenderTvHeatmap();
      }
      if (tvOiChart) {
        tvOiChart.timeScale().fitContent();
      }
      if (tvFundingChart) {
        tvFundingChart.timeScale().fitContent();
      }
    }

    function getLiqScopePaletteColors(ratio, isLong, isMax, palette) {
      // Base alpha scaled by non-linear ratio
      const alpha = Math.min(0.92, 0.20 + ratio * 0.72);

      if (palette === 'longshort') {
        if (isLong) {
          const g = Math.round(180 + ratio * 75);
          return {
            ribbonStart: `rgba(0, 100, 50, ${alpha * 0.15})`,
            ribbonMid: `rgba(0, ${g}, 100, ${alpha * 0.45})`,
            ribbonCore: `rgba(0, 240, 140, ${alpha * 0.85})`,
            ribbonEnd: `rgba(160, 255, 200, ${alpha * 0.95})`,
            glowLine: `rgba(0, 255, 150, ${Math.min(1, alpha + 0.2)})`,
            profileBar: `rgba(0, 230, 130, ${Math.min(0.95, alpha + 0.1)})`,
            profileBorder: '#00f090',
          };
        } else {
          const r = Math.round(200 + ratio * 55);
          return {
            ribbonStart: `rgba(100, 20, 30, ${alpha * 0.15})`,
            ribbonMid: `rgba(${r}, 40, 60, ${alpha * 0.45})`,
            ribbonCore: `rgba(255, 60, 80, ${alpha * 0.85})`,
            ribbonEnd: `rgba(255, 140, 80, ${alpha * 0.95})`,
            glowLine: `rgba(255, 80, 100, ${Math.min(1, alpha + 0.2)})`,
            profileBar: `rgba(255, 51, 88, ${Math.min(0.95, alpha + 0.1)})`,
            profileBorder: '#ff3358',
          };
        }
      }

      if (palette === 'plasma') {
        if (ratio < 0.25) {
          return {
            ribbonStart: `rgba(40, 10, 80, ${alpha * 0.2})`,
            ribbonMid: `rgba(80, 20, 140, ${alpha * 0.5})`,
            ribbonCore: `rgba(140, 30, 200, ${alpha * 0.75})`,
            ribbonEnd: `rgba(180, 50, 240, ${alpha * 0.85})`,
            glowLine: 'rgba(160, 40, 230, 0.6)',
            profileBar: 'rgba(140, 30, 200, 0.7)',
            profileBorder: '#9933ff',
          };
        } else if (ratio < 0.60) {
          return {
            ribbonStart: `rgba(60, 20, 120, ${alpha * 0.25})`,
            ribbonMid: `rgba(180, 30, 180, ${alpha * 0.55})`,
            ribbonCore: `rgba(255, 40, 160, ${alpha * 0.85})`,
            ribbonEnd: `rgba(255, 100, 200, ${alpha * 0.95})`,
            glowLine: 'rgba(255, 60, 180, 0.8)',
            profileBar: 'rgba(255, 40, 160, 0.85)',
            profileBorder: '#ff2df0',
          };
        } else {
          return {
            ribbonStart: `rgba(100, 30, 180, ${alpha * 0.3})`,
            ribbonMid: `rgba(240, 50, 180, ${alpha * 0.6})`,
            ribbonCore: `rgba(0, 240, 255, ${alpha * 0.9})`,
            ribbonEnd: `rgba(255, 255, 255, ${alpha})`,
            glowLine: 'rgba(0, 255, 255, 0.95)',
            profileBar: 'rgba(0, 229, 255, 0.9)',
            profileBorder: '#00e5ff',
          };
        }
      }

      // Default: 🔥 LIQSCOPE TURBO
      if (ratio < 0.18) {
        // Deep Indigo/Navy (Bajo)
        return {
          ribbonStart: `rgba(15, 25, 75, ${alpha * 0.2})`,
          ribbonMid: `rgba(25, 40, 120, ${alpha * 0.45})`,
          ribbonCore: `rgba(35, 65, 180, ${alpha * 0.7})`,
          ribbonEnd: `rgba(45, 90, 220, ${alpha * 0.8})`,
          glowLine: 'rgba(40, 80, 200, 0.4)',
          profileBar: 'rgba(30, 60, 160, 0.65)',
          profileBorder: '#2341b4',
        };
      } else if (ratio < 0.42) {
        // Electric Cyan (Medio-Bajo)
        return {
          ribbonStart: `rgba(10, 45, 100, ${alpha * 0.25})`,
          ribbonMid: `rgba(0, 130, 210, ${alpha * 0.55})`,
          ribbonCore: `rgba(0, 195, 255, ${alpha * 0.85})`,
          ribbonEnd: `rgba(60, 225, 255, ${alpha * 0.95})`,
          glowLine: 'rgba(0, 210, 255, 0.75)',
          profileBar: 'rgba(0, 185, 245, 0.8)',
          profileBorder: '#00bfff',
        };
      } else if (ratio < 0.68) {
        // Lime / Neon Green (Medio-Alto)
        return {
          ribbonStart: `rgba(15, 60, 80, ${alpha * 0.3})`,
          ribbonMid: `rgba(20, 160, 100, ${alpha * 0.6})`,
          ribbonCore: `rgba(45, 225, 85, ${alpha * 0.9})`,
          ribbonEnd: `rgba(110, 255, 120, ${alpha * 0.98})`,
          glowLine: 'rgba(50, 240, 90, 0.85)',
          profileBar: 'rgba(40, 220, 80, 0.85)',
          profileBorder: '#39ff14',
        };
      } else if (ratio < 0.88) {
        // Solar Gold / Neon Yellow (Alto)
        return {
          ribbonStart: `rgba(30, 70, 40, ${alpha * 0.35})`,
          ribbonMid: `rgba(160, 170, 20, ${alpha * 0.7})`,
          ribbonCore: `rgba(255, 215, 0, ${alpha * 0.95})`,
          ribbonEnd: `rgba(255, 240, 60, 1.0)`,
          glowLine: 'rgba(255, 220, 10, 0.95)',
          profileBar: 'rgba(255, 210, 0, 0.9)',
          profileBorder: '#ffd700',
        };
      } else {
        // Incandescent White-Hot / Golden Epicenter (Ultra Alto)
        return {
          ribbonStart: `rgba(60, 70, 20, ${alpha * 0.4})`,
          ribbonMid: `rgba(220, 180, 20, ${alpha * 0.8})`,
          ribbonCore: `rgba(255, 250, 150, 1.0)`,
          ribbonEnd: `rgba(255, 255, 255, 1.0)`,
          glowLine: '#ffffff',
          profileBar: 'rgba(255, 245, 160, 0.98)',
          profileBorder: '#ffffff',
        };
      }
    }

    function renderTvHeatmap() {
      const canvas = document.getElementById('tv-heatmap-canvas');
      const container = document.getElementById('tv-chart-canvas');
      if (!canvas || !container || !tvCandleSeries) return;

      syncCanvasSize();

      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const w = container.clientWidth;
      const h = container.clientHeight;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      if (!tvOverlaysEnabled || !currentData || !currentData.bins || currentData.bins.length === 0) {
        return;
      }

      const bins = currentData.bins;
      const mark = currentData.current_price;
      const maxVol = Math.max(...bins.map(b => b.estimated_volume_usd), 1);

      // Identify the MAX LIQ POOL epicenter
      let maxLiqBin = bins[0];
      bins.forEach(b => {
        if (b.estimated_volume_usd > maxLiqBin.estimated_volume_usd) maxLiqBin = b;
      });

      // Price scale right margin in Lightweight Charts is ~55-65px
      const priceScaleMargin = 60;
      const chartAreaWidth = Math.max(80, w - priceScaleMargin);
      const profileMaxBarWidth = Math.min(140, chartAreaWidth * 0.28);
      const profileStartX = chartAreaWidth - 4;

      // 1. RENDER CONTINUOUS LIQSCOPE HEATMAP BANDS & DEPTH PROFILE
      bins.forEach(bin => {
        const vol = bin.estimated_volume_usd;
        if (vol <= 0) return;

        const yMid = tvCandleSeries.priceToCoordinate(bin.price_mid);
        if (yMid === null || isNaN(yMid)) return;

        let yTop = tvCandleSeries.priceToCoordinate(bin.price_max);
        let yBottom = tvCandleSeries.priceToCoordinate(bin.price_min);

        let bandHeight;
        let bandY;
        if (yTop !== null && yBottom !== null && !isNaN(yTop) && !isNaN(yBottom)) {
          bandHeight = Math.max(5, Math.abs(yBottom - yTop));
          bandY = Math.min(yTop, yBottom);
        } else {
          bandHeight = 7;
          bandY = yMid - 3.5;
        }

        // Skip bins outside the visible vertical viewport
        if (bandY + bandHeight < 0 || bandY > h) return;

        const rawRatio = Math.min(1.0, vol / maxVol);
        const gammaRatio = Math.pow(rawRatio, 0.65) * tvIntensityMultiplier;
        const ratio = Math.max(0.05, Math.min(1.0, gammaRatio));

        const isLong = bin.price_mid < mark;
        const isMax = (maxLiqBin && bin.price_mid === maxLiqBin.price_mid);

        const colors = getLiqScopePaletteColors(ratio, isLong, isMax, tvPalette);

        // Continuous Heat Corridor: Left-to-right gradient
        const ribbonGrad = ctx.createLinearGradient(0, bandY, chartAreaWidth, bandY);
        ribbonGrad.addColorStop(0, colors.ribbonStart);
        ribbonGrad.addColorStop(0.35, colors.ribbonMid);
        ribbonGrad.addColorStop(0.82, colors.ribbonCore);
        ribbonGrad.addColorStop(1, colors.ribbonEnd);

        ctx.fillStyle = ribbonGrad;
        ctx.fillRect(0, bandY, chartAreaWidth, bandHeight);

        // Core glow filament for dense clusters
        if (ratio > 0.45) {
          ctx.fillStyle = colors.glowLine;
          ctx.fillRect(0, bandY + bandHeight / 2 - 0.5, chartAreaWidth, 1);
        }

        // Right-Side Horizontal Liquidation Volume Profile Bar
        const barWidth = Math.max(4, rawRatio * profileMaxBarWidth);
        const barX = profileStartX - barWidth;
        const barHeight = Math.max(4, bandHeight - 1);
        const barY = Math.max(0, yMid - barHeight / 2);

        ctx.fillStyle = colors.profileBar;
        if (ctx.roundRect) {
          ctx.beginPath();
          ctx.roundRect(barX, barY, barWidth, barHeight, [3, 0, 0, 3]);
          ctx.fill();
        } else {
          ctx.fillRect(barX, barY, barWidth, barHeight);
        }

        ctx.strokeStyle = colors.profileBorder;
        ctx.lineWidth = 1;
        ctx.stroke();

        // Volume text tag on top clusters for instant quantitative reading
        if (rawRatio > 0.28 && w > 480) {
          const volM = (vol / 1e6).toFixed(vol >= 1e9 ? 2 : 0);
          const unit = vol >= 1e9 ? 'B' : 'M';
          const levStr = bin.dominant_leverage ? ` ${bin.dominant_leverage}x` : '';
          const textLabel = `$${volM}${unit}${levStr}`;

          ctx.font = '9px JetBrains Mono, monospace';
          ctx.fillStyle = '#ffffff';
          ctx.textAlign = 'right';
          ctx.textBaseline = 'middle';

          ctx.shadowColor = '#000000';
          ctx.shadowBlur = 4;
          ctx.fillText(textLabel, barX - 4, yMid);
          ctx.shadowBlur = 0;
        }
      });

      // 2. MAX LIQUIDATION EPICENTER POOL HIGHLIGHT (🎯 LIQSCOPE FOCO)
      if (maxLiqBin) {
        const yMax = tvCandleSeries.priceToCoordinate(maxLiqBin.price_mid);
        if (yMax !== null && !isNaN(yMax) && yMax >= 0 && yMax <= h) {
          ctx.save();
          ctx.strokeStyle = '#ffd700';
          ctx.lineWidth = 2;
          ctx.setLineDash([5, 4]);
          ctx.shadowColor = '#ffd700';
          ctx.shadowBlur = 8;
          ctx.beginPath();
          ctx.moveTo(0, yMax);
          ctx.lineTo(chartAreaWidth, yMax);
          ctx.stroke();
          ctx.restore();

          // Golden badge tag
          const maxVolM = (maxLiqBin.estimated_volume_usd / 1e6).toFixed(0);
          const badgeText = `🎯 MAX LIQ POOL: $${maxVolM}M (${maxLiqBin.dominant_leverage || 50}x)`;
          ctx.font = 'bold 10px JetBrains Mono, monospace';
          const textW = ctx.measureText(badgeText).width;

          ctx.fillStyle = 'rgba(7, 9, 14, 0.90)';
          ctx.strokeStyle = '#ffd700';
          ctx.lineWidth = 1;
          ctx.beginPath();
          if (ctx.roundRect) {
            ctx.roundRect(10, yMax - 10, textW + 14, 20, 4);
          } else {
            ctx.rect(10, yMax - 10, textW + 14, 20);
          }
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = '#ffd700';
          ctx.textAlign = 'left';
          ctx.textBaseline = 'middle';
          ctx.fillText(badgeText, 17, yMax);
        }
      }

      // 3. MARK PRICE LASER HORIZONTAL GUIDE
      const yMark = tvCandleSeries.priceToCoordinate(mark);
      if (yMark !== null && !isNaN(yMark) && yMark >= 0 && yMark <= h) {
        ctx.save();
        ctx.strokeStyle = 'rgba(0, 229, 255, 0.75)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([3, 3]);
        ctx.shadowColor = '#00e5ff';
        ctx.shadowBlur = 4;
        ctx.beginPath();
        ctx.moveTo(0, yMark);
        ctx.lineTo(chartAreaWidth, yMark);
        ctx.stroke();
        ctx.restore();
      }
    }

    function initTradingViewChart() {
      const container = document.getElementById('tv-chart-canvas');
      const lwContainer = document.getElementById('tv-lw-container');
      if (!container || !lwContainer || typeof LightweightCharts === 'undefined') {
        console.warn('TradingView library not loaded yet or container missing.');
        return;
      }

      if (tvChart) {
        tvChart.remove();
        tvChart = null;
      }

      syncCanvasSize();

      const isMobile = window.innerWidth < 640;
      const chartHeight = isMobile ? 440 : 520;

      tvChart = LightweightCharts.createChart(lwContainer, {
        width: lwContainer.clientWidth || container.clientWidth || 600,
        height: chartHeight,
        layout: {
          background: { type: 'solid', color: 'transparent' },
          textColor: '#8e9bb5',
          fontSize: 11,
          fontFamily: 'JetBrains Mono, monospace',
        },
        grid: {
          vertLines: { color: 'rgba(27, 37, 59, 0.35)' },
          horzLines: { color: 'rgba(27, 37, 59, 0.35)' },
        },
        crosshair: {
          mode: LightweightCharts.CrosshairMode.Normal,
          vertLine: {
            color: '#00e5ff',
            width: 1,
            style: LightweightCharts.LineStyle.Dashed,
            labelBackgroundColor: '#0d111a',
          },
          horzLine: {
            color: '#00e5ff',
            width: 1,
            style: LightweightCharts.LineStyle.Dashed,
            labelBackgroundColor: '#0d111a',
          },
        },
        rightPriceScale: {
          borderColor: 'rgba(27, 37, 59, 0.8)',
          scaleMargins: {
            top: 0.08,
            bottom: 0.18,
          },
        },
        timeScale: {
          borderColor: 'rgba(27, 37, 59, 0.8)',
          timeVisible: true,
          secondsVisible: false,
        },
        handleScroll: {
          mouseWheel: true,
          pressedMouseMove: true,
          horzTouchDrag: true,
          vertTouchDrag: false,
        },
        handleScale: {
          axisPressedMouseMove: true,
          mouseWheel: true,
          pinch: true,
        },
      });

      // 1. Candlestick Series (Cyber OLED Palette)
      tvCandleSeries = tvChart.addCandlestickSeries({
        upColor: '#00f090',
        downColor: '#ff3358',
        borderUpColor: '#00f090',
        borderDownColor: '#ff3358',
        wickUpColor: '#00f090',
        wickDownColor: '#ff3358',
      });

      // 2. Volume Histogram Series (Below price)
      tvVolumeSeries = tvChart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '', // overlay
        scaleMargins: {
          top: 0.84,
          bottom: 0,
        },
      });

      // Synchronize Heatmap canvas & sub-charts on scroll & zoom
      tvChart.timeScale().subscribeVisibleLogicalRangeChange(range => {
        requestRenderTvHeatmap();
        if (isSyncingSubRanges || !range) return;
        isSyncingSubRanges = true;
        try {
          if (tvOiChart && tvSubOiEnabled) tvOiChart.timeScale().setVisibleLogicalRange(range);
          if (tvFundingChart && tvSubFundingEnabled) tvFundingChart.timeScale().setVisibleLogicalRange(range);
        } catch (e) {}
        isSyncingSubRanges = false;
      });
      tvChart.timeScale().subscribeVisibleTimeRangeChange(() => requestRenderTvHeatmap());

      // User interaction listeners on container (wheel zoom, drag pan)
      container.addEventListener('wheel', () => requestRenderTvHeatmap(), { passive: true });
      container.addEventListener('mousemove', (e) => {
        if (e.buttons > 0) requestRenderTvHeatmap();
      });
      container.addEventListener('touchmove', () => requestRenderTvHeatmap(), { passive: true });

      // 3. Crosshair HUD Telemetry Subscription
      tvChart.subscribeCrosshairMove(param => {
        if (!param || !param.time || !param.seriesData.has(tvCandleSeries)) {
          updateTvHudDefault();
          return;
        }

        const candle = param.seriesData.get(tvCandleSeries);
        const volume = param.seriesData.get(tvVolumeSeries);

        if (candle) {
          const oEl = document.getElementById('hud-open');
          const hEl = document.getElementById('hud-high');
          const lEl = document.getElementById('hud-low');
          const cEl = document.getElementById('hud-close');
          const vEl = document.getElementById('hud-vol');

          if (oEl) oEl.innerText = `$${candle.open.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
          if (hEl) hEl.innerText = `$${candle.high.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
          if (lEl) lEl.innerText = `$${candle.low.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
          if (cEl) cEl.innerText = `$${candle.close.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
          if (vEl && volume) vEl.innerText = `${volume.value.toLocaleString('en-US', { maximumFractionDigits: 1 })}`;
        }

        // Crosshair sync to sub-panels
        if (tvSubOiEnabled && tvOiData && tvOiData.length > 0) {
          const oiPoint = tvOiData.find(d => d.time === param.time);
          if (oiPoint) {
            const valB = (oiPoint.value / 1e9).toFixed(3);
            const coinsStr = oiPoint.coins ? ` (${oiPoint.coins.toLocaleString('en-US', { maximumFractionDigits: 0 })} ${currentSymbol.replace('USDT','')})` : '';
            const subOiHud = document.getElementById('sub-oi-hud-val');
            if (subOiHud) subOiHud.innerHTML = `$${valB}B USD${coinsStr}`;
          }
        }
        if (tvSubFundingEnabled && tvFundingData && tvFundingData.length > 0) {
          const fPoint = tvFundingData.slice().reverse().find(d => Math.abs(d.time - param.time) <= 14400) || tvFundingData[tvFundingData.length - 1];
          if (fPoint) {
            const pct = fPoint.value.toFixed(4);
            const color = fPoint.value >= 0 ? 'text-[#00f090]' : 'text-[#ff3358]';
            const tag = fPoint.value >= 0 ? '🟢 Longs pagan' : '🔴 Shorts pagan';
            const subFHud = document.getElementById('sub-funding-hud-val');
            if (subFHud) subFHud.innerHTML = `<span class="${color} font-bold">${fPoint.value > 0 ? '+' : ''}${pct}%</span> <span class="text-[9px] text-outline font-normal">(${tag})</span>`;
          }
        }
      });

      // Auto-resize on window changes
      const resizeObserver = new ResizeObserver(entries => {
        if (tvChart && container.clientWidth > 0) {
          const w = container.clientWidth;
          const h = isMobile ? 440 : 520;
          tvChart.applyOptions({ width: w, height: h });
          syncCanvasSize();
          requestRenderTvHeatmap();
        }
        if (tvOiChart) {
          const oiC = document.getElementById('tv-subchart-oi-container');
          if (oiC && oiC.clientWidth > 0) tvOiChart.applyOptions({ width: oiC.clientWidth });
        }
        if (tvFundingChart) {
          const fC = document.getElementById('tv-subchart-funding-container');
          if (fC && fC.clientWidth > 0) tvFundingChart.applyOptions({ width: fC.clientWidth });
        }
      });
      resizeObserver.observe(container);

      // Initial Fetch
      fetchKlinesAndRender(currentSymbol, tvTimeframe);
    }

    function updateTvHudDefault() {
      if (!tvKlinesData || tvKlinesData.length === 0) return;
      const last = tvKlinesData[tvKlinesData.length - 1];
      const oEl = document.getElementById('hud-open');
      const hEl = document.getElementById('hud-high');
      const lEl = document.getElementById('hud-low');
      const cEl = document.getElementById('hud-close');
      const vEl = document.getElementById('hud-vol');

      if (oEl) oEl.innerText = `$${last.open.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      if (hEl) hEl.innerText = `$${last.high.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      if (lEl) lEl.innerText = `$${last.low.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      if (cEl) cEl.innerText = `$${last.close.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      if (vEl) vEl.innerText = `${last.volume.toLocaleString('en-US', { maximumFractionDigits: 1 })}`;

      updateSubOiHudDefault();
      updateSubFundingHudDefault();
    }

    function updateSubOiHudDefault() {
      const hud = document.getElementById('sub-oi-hud-val');
      if (!hud || !tvOiData || tvOiData.length === 0) return;
      const last = tvOiData[tvOiData.length - 1];
      const valB = (last.value / 1e9).toFixed(3);
      const coinsStr = last.coins ? ` (${last.coins.toLocaleString('en-US', { maximumFractionDigits: 0 })} ${currentSymbol.replace('USDT','')})` : '';
      hud.innerHTML = `$${valB}B USD${coinsStr}`;
    }

    function updateSubFundingHudDefault() {
      const hud = document.getElementById('sub-funding-hud-val');
      if (!hud || !tvFundingData || tvFundingData.length === 0) return;
      const last = tvFundingData[tvFundingData.length - 1];
      const pct = last.value.toFixed(4);
      const color = last.value >= 0 ? 'text-[#00f090]' : 'text-[#ff3358]';
      const tag = last.value >= 0 ? '🟢 Longs pagan' : '🔴 Shorts pagan';
      hud.innerHTML = `<span class="${color} font-bold">${last.value > 0 ? '+' : ''}${pct}%</span> <span class="text-[9px] text-outline font-normal">(${tag})</span>`;
    }

    async function fetchKlinesAndRender(symbol, interval) {
      const hudSym = document.getElementById('hud-symbol');
      if (hudSym) hudSym.innerText = `${symbol} ${interval.toUpperCase()} [${currentTimeframeHorizon.toUpperCase()}]`;

      // Parallel fetch for sub-panels if enabled
      if (tvSubOiEnabled) fetchSubOiData(symbol, interval);
      if (tvSubFundingEnabled) fetchSubFundingData(symbol);

      try {
        const resp = await fetch(`/api/v1/klines/${symbol}?interval=${interval}&limit=120`);
        if (resp.ok) {
          const klines = await resp.json();
          if (Array.isArray(klines) && klines.length > 0) {
            tvKlinesData = klines;
            if (tvCandleSeries && tvVolumeSeries) {
              tvCandleSeries.setData(klines);

              const volData = klines.map(k => ({
                time: k.time,
                value: k.volume,
                color: k.close >= k.open ? 'rgba(0, 240, 144, 0.25)' : 'rgba(255, 51, 88, 0.25)',
              }));
              tvVolumeSeries.setData(volData);

              updateTvHudDefault();

              // Trigger heatmap re-render with fresh coordinates
              setTimeout(() => {
                requestRenderTvHeatmap();
              }, 20);
            }
          }
        }
      } catch (err) {
        console.warn('Fallo al obtener velas de TradingView:', err);
      }
    }

    function changeTvTimeframe(tf) {
      tvTimeframe = tf;
      ['15m', '1h', '4h', '1d'].forEach(item => {
        const btn = document.getElementById(`tf-${item}`);
        if (btn) {
          if (item === tf) {
            btn.className = 'px-2 py-0.5 rounded text-[11px] font-mono font-bold text-mark bg-surface-card border border-mark/30 transition-all cursor-pointer shadow-xs';
          } else {
            btn.className = 'px-2 py-0.5 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer';
          }
        }
      });
      fetchKlinesAndRender(currentSymbol, tf);
    }

    function toggleTvLiquidationOverlays() {
      tvOverlaysEnabled = !tvOverlaysEnabled;
      const btn = document.getElementById('btn-toggle-tv-overlays');
      const text = document.getElementById('tv-overlay-text');
      const hudActive = document.getElementById('hud-active-wall');
      const legend = document.getElementById('tv-liqscope-legend');

      if (btn && text) {
        if (tvOverlaysEnabled) {
          btn.className = 'px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-mark bg-mark/10 border border-mark/25 flex items-center gap-1 transition-all cursor-pointer';
          text.innerText = 'Heatmap: ON';
          if (hudActive) hudActive.innerText = 'Heatmap LiqScope: Activo';
          if (legend) legend.style.display = 'flex';
        } else {
          btn.className = 'px-2.5 py-1 rounded-lg text-xs font-mono font-semibold text-outline bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer';
          text.innerText = 'Heatmap: OFF';
          if (hudActive) hudActive.innerText = 'Heatmap LiqScope: Desactivado';
          if (legend) legend.style.display = 'none';
        }
      }

      requestRenderTvHeatmap();
    }

    function renderLiquidationOverlaysOnTV(data) {
      if (!tvCandleSeries) return;

      // Clean legacy price lines if any exist
      tvActivePriceLines.forEach(line => {
        try {
          tvCandleSeries.removePriceLine(line);
        } catch (e) {}
      });
      tvActivePriceLines = [];

      requestRenderTvHeatmap();
    }

    // ==============================================================
    // SÚPER GRÁFICOS: SUB-PANELES SINCRONIZADOS (OI & FUNDING HISTÓRICO)
    // ==============================================================
    function initTvSubOiChart() {
      const container = document.getElementById('tv-sub-oi-lw');
      if (!container || typeof LightweightCharts === 'undefined') return;

      if (tvOiChart) {
        try { tvOiChart.remove(); } catch(e) {}
        tvOiChart = null;
        tvOiSeries = null;
      }

      tvOiChart = LightweightCharts.createChart(container, {
        width: container.clientWidth || 600,
        height: 130,
        layout: {
          background: { type: 'solid', color: 'transparent' },
          textColor: '#8e9bb5',
          fontSize: 10,
          fontFamily: 'JetBrains Mono, monospace',
        },
        grid: {
          vertLines: { color: 'rgba(27, 37, 59, 0.25)' },
          horzLines: { color: 'rgba(27, 37, 59, 0.25)' },
        },
        timeScale: {
          borderColor: 'rgba(27, 37, 59, 0.8)',
          timeVisible: true,
          secondsVisible: false,
          visible: false,
        },
        rightPriceScale: {
          borderColor: 'rgba(27, 37, 59, 0.8)',
          scaleMargins: {
            top: 0.15,
            bottom: 0.1,
          },
        },
        crosshair: {
          mode: LightweightCharts.CrosshairMode.Normal,
          vertLine: {
            color: '#00e5ff',
            width: 1,
            style: LightweightCharts.LineStyle.Dashed,
            labelBackgroundColor: '#0d111a',
          },
          horzLine: {
            color: '#00e5ff',
            width: 1,
            style: LightweightCharts.LineStyle.Dashed,
            labelBackgroundColor: '#0d111a',
          },
        },
        handleScroll: {
          mouseWheel: true,
          pressedMouseMove: true,
          horzTouchDrag: true,
          vertTouchDrag: false,
        },
        handleScale: {
          axisPressedMouseMove: true,
          mouseWheel: true,
          pinch: true,
        },
      });

      tvOiSeries = tvOiChart.addAreaSeries({
        topColor: 'rgba(0, 229, 255, 0.35)',
        bottomColor: 'rgba(0, 229, 255, 0.02)',
        lineColor: '#00e5ff',
        lineWidth: 2,
        priceFormat: {
          type: 'custom',
          formatter: price => {
            if (price >= 1e9) return `$${(price / 1e9).toFixed(2)}B`;
            if (price >= 1e6) return `$${(price / 1e6).toFixed(1)}M`;
            return `$${price.toLocaleString('en-US')}`;
          },
        },
      });

      tvOiChart.timeScale().subscribeVisibleLogicalRangeChange(range => {
        if (isSyncingSubRanges || !range || !tvChart) return;
        isSyncingSubRanges = true;
        try {
          tvChart.timeScale().setVisibleLogicalRange(range);
        } catch(e) {}
        if (tvFundingChart && tvSubFundingEnabled) {
          try { tvFundingChart.timeScale().setVisibleLogicalRange(range); } catch(e) {}
        }
        isSyncingSubRanges = false;
        requestRenderTvHeatmap();
      });

      tvOiChart.subscribeCrosshairMove(param => {
        const hud = document.getElementById('sub-oi-hud-val');
        if (!hud) return;
        if (!param || !param.time || !param.seriesData.has(tvOiSeries)) {
          updateSubOiHudDefault();
          return;
        }
        const point = param.seriesData.get(tvOiSeries);
        if (point) {
          const valB = (point.value / 1e9).toFixed(3);
          const found = tvOiData.find(d => d.time === param.time);
          const coinsStr = found && found.coins ? ` (${found.coins.toLocaleString('en-US', { maximumFractionDigits: 0 })} ${currentSymbol.replace('USDT','')})` : '';
          hud.innerHTML = `$${valB}B USD${coinsStr}`;
        }
      });
    }

    function initTvSubFundingChart() {
      const container = document.getElementById('tv-sub-funding-lw');
      if (!container || typeof LightweightCharts === 'undefined') return;

      if (tvFundingChart) {
        try { tvFundingChart.remove(); } catch(e) {}
        tvFundingChart = null;
        tvFundingHistSeries = null;
      }

      tvFundingChart = LightweightCharts.createChart(container, {
        width: container.clientWidth || 600,
        height: 115,
        layout: {
          background: { type: 'solid', color: 'transparent' },
          textColor: '#8e9bb5',
          fontSize: 10,
          fontFamily: 'JetBrains Mono, monospace',
        },
        grid: {
          vertLines: { color: 'rgba(27, 37, 59, 0.25)' },
          horzLines: { color: 'rgba(27, 37, 59, 0.25)' },
        },
        timeScale: {
          borderColor: 'rgba(27, 37, 59, 0.8)',
          timeVisible: true,
          secondsVisible: false,
          visible: true,
        },
        rightPriceScale: {
          borderColor: 'rgba(27, 37, 59, 0.8)',
          scaleMargins: {
            top: 0.2,
            bottom: 0.15,
          },
        },
        crosshair: {
          mode: LightweightCharts.CrosshairMode.Normal,
          vertLine: {
            color: '#00e5ff',
            width: 1,
            style: LightweightCharts.LineStyle.Dashed,
            labelBackgroundColor: '#0d111a',
          },
          horzLine: {
            color: '#00e5ff',
            width: 1,
            style: LightweightCharts.LineStyle.Dashed,
            labelBackgroundColor: '#0d111a',
          },
        },
        handleScroll: {
          mouseWheel: true,
          pressedMouseMove: true,
          horzTouchDrag: true,
          vertTouchDrag: false,
        },
        handleScale: {
          axisPressedMouseMove: true,
          mouseWheel: true,
          pinch: true,
        },
      });

      tvFundingHistSeries = tvFundingChart.addHistogramSeries({
        priceFormat: {
          type: 'custom',
          formatter: price => `${price.toFixed(4)}%`,
        },
        base: 0,
      });

      tvFundingChart.timeScale().subscribeVisibleLogicalRangeChange(range => {
        if (isSyncingSubRanges || !range || !tvChart) return;
        isSyncingSubRanges = true;
        try {
          tvChart.timeScale().setVisibleLogicalRange(range);
        } catch(e) {}
        if (tvOiChart && tvSubOiEnabled) {
          try { tvOiChart.timeScale().setVisibleLogicalRange(range); } catch(e) {}
        }
        isSyncingSubRanges = false;
        requestRenderTvHeatmap();
      });

      tvFundingChart.subscribeCrosshairMove(param => {
        const hud = document.getElementById('sub-funding-hud-val');
        if (!hud) return;
        if (!param || !param.time || !param.seriesData.has(tvFundingHistSeries)) {
          updateSubFundingHudDefault();
          return;
        }
        const point = param.seriesData.get(tvFundingHistSeries);
        if (point) {
          const pct = point.value.toFixed(4);
          const color = point.value >= 0 ? 'text-[#00f090]' : 'text-[#ff3358]';
          const tag = point.value >= 0 ? '🟢 Longs pagan' : '🔴 Shorts pagan';
          hud.innerHTML = `<span class="${color} font-bold">${point.value > 0 ? '+' : ''}${pct}%</span> <span class="text-[9px] text-outline font-normal">(${tag})</span>`;
        }
      });
    }

    async function fetchSubOiData(symbol, interval) {
      if (!tvSubOiEnabled) return;
      try {
        const res = await fetch(`/api/v1/klines/${symbol}/open-interest?interval=${interval}&limit=120`);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            tvOiData = data;
            if (tvOiSeries) {
              tvOiSeries.setData(data);
              updateSubOiHudDefault();
              if (tvChart && tvOiChart) {
                const range = tvChart.timeScale().getVisibleLogicalRange();
                if (range) {
                  try { tvOiChart.timeScale().setVisibleLogicalRange(range); } catch(e) {}
                }
              }
            }
          }
        }
      } catch (err) {
        console.warn('Fallo al obtener Open Interest histórico:', err);
      }
    }

    async function fetchSubFundingData(symbol) {
      if (!tvSubFundingEnabled) return;
      try {
        const res = await fetch(`/api/v1/klines/${symbol}/funding-history?limit=120`);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            tvFundingData = data;
            if (tvFundingHistSeries) {
              tvFundingHistSeries.setData(data);
              updateSubFundingHudDefault();
              if (tvChart && tvFundingChart) {
                const range = tvChart.timeScale().getVisibleLogicalRange();
                if (range) {
                  try { tvFundingChart.timeScale().setVisibleLogicalRange(range); } catch(e) {}
                }
              }
            }
          }
        }
      } catch (err) {
        console.warn('Fallo al obtener histórico de funding rates:', err);
      }
    }

    function toggleTvSubChart(type) {
      if (type === 'oi') {
        tvSubOiEnabled = !tvSubOiEnabled;
        const container = document.getElementById('tv-subchart-oi-container');
        const btn = document.getElementById('btn-toggle-sub-oi');
        if (container) {
          if (tvSubOiEnabled) {
            container.classList.remove('hidden');
            if (btn) {
              btn.className = 'px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-cyan-400 bg-cyan-400/10 border border-cyan-400/30 flex items-center gap-1 transition-all cursor-pointer shadow-xs';
            }
            initTvSubOiChart();
            fetchSubOiData(currentSymbol, tvTimeframe);
          } else {
            container.classList.add('hidden');
            if (btn) {
              btn.className = 'px-2.5 py-1 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer';
            }
            if (tvOiChart) {
              try { tvOiChart.remove(); } catch(e) {}
              tvOiChart = null;
              tvOiSeries = null;
            }
          }
        }
      } else if (type === 'funding') {
        tvSubFundingEnabled = !tvSubFundingEnabled;
        const container = document.getElementById('tv-subchart-funding-container');
        const btn = document.getElementById('btn-toggle-sub-funding');
        if (container) {
          if (tvSubFundingEnabled) {
            container.classList.remove('hidden');
            if (btn) {
              btn.className = 'px-2.5 py-1 rounded-lg text-xs font-mono font-bold text-amber-400 bg-amber-400/10 border border-amber-400/30 flex items-center gap-1 transition-all cursor-pointer shadow-xs';
            }
            initTvSubFundingChart();
            fetchSubFundingData(currentSymbol);
          } else {
            container.classList.add('hidden');
            if (btn) {
              btn.className = 'px-2.5 py-1 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer';
            }
            if (tvFundingChart) {
              try { tvFundingChart.remove(); } catch(e) {}
              tvFundingChart = null;
              tvFundingHistSeries = null;
            }
          }
        }
      }
    }

    // ==========================================
    // FUNDING RATES (TASAS DE FINANCIACIÓN) ENGINE
    // ==========================================
    let fundingMatrixData = null;
    let fundingFilter = 'all'; // 'all', 'overheated', 'longs_pay', 'shorts_pay'
    let fundingCountdownSec = 0;
    let fundingTimerInterval = null;

    async function fetchFundingRates() {
      try {
        const resp = await fetch('/api/v1/funding');
        if (resp.ok) {
          const data = await resp.json();
          fundingMatrixData = data;
          renderFundingUI(data);
          updateTelemetryFundingBadge(data);
        }
      } catch (err) {
        console.warn('Error al obtener tasas de financiación:', err);
      }
    }

    function updateTelemetryFundingBadge(data) {
      if (!data || !data.items) return;
      const btc = data.items.find(i => i.symbol === currentSymbol) || data.items[0];
      if (!btc) return;

      const ratePill = document.getElementById('metric-funding-rate');
      const hudPill = document.getElementById('hud-funding-rate');
      const topPill = document.getElementById('top-funding-pill');

      const rateStr = `${btc.average_rate >= 0 ? '+' : ''}${btc.average_rate.toFixed(4)}%`;
      if (ratePill) ratePill.innerHTML = `${rateStr} <span class="text-outline text-[10px]">8h</span>`;
      if (hudPill) hudPill.innerText = `Funding: ${rateStr} (8h)`;
      if (topPill) topPill.innerText = rateStr;
    }

    function renderFundingUI(data) {
      if (!data) return;

      fundingCountdownSec = data.seconds_until_funding || 0;
      updateFundingClockUI();
      if (!fundingTimerInterval) {
        fundingTimerInterval = setInterval(() => {
          if (fundingCountdownSec > 0) {
            fundingCountdownSec--;
            updateFundingClockUI();
          }
        }, 1000);
      }

      const btc = data.items.find(i => i.symbol === 'BTCUSDT');
      if (btc) {
        const avg = document.getElementById('card-btc-avg-rate');
        const apr = document.getElementById('card-btc-apr');
        const bin = document.getElementById('card-btc-binance');
        const byb = document.getElementById('card-btc-bybit');
        const bias = document.getElementById('card-btc-bias-pill');

        if (avg) {
          avg.innerText = `${btc.average_rate >= 0 ? '+' : ''}${btc.average_rate.toFixed(4)}%`;
          avg.className = btc.average_rate > 0.02 ? 'text-lg font-mono font-black text-amber-400' : 'text-lg font-mono font-black text-cyan-400';
        }
        if (apr) apr.innerText = `${btc.annualized_apr >= 0 ? '+' : ''}${btc.annualized_apr.toFixed(2)}%`;
        if (bin) bin.innerText = `${btc.binance_rate >= 0 ? '+' : ''}${btc.binance_rate.toFixed(4)}%`;
        if (byb) byb.innerText = `${btc.bybit_rate >= 0 ? '+' : ''}${btc.bybit_rate.toFixed(4)}%`;
        if (bias) {
          bias.innerText = btc.bias === 'LONGS_PAY' ? 'Longs pagan' : (btc.bias === 'SHORTS_PAY' ? 'Shorts pagan' : 'Neutral');
          bias.className = btc.bias === 'LONGS_PAY' ? 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-long/15 text-long border border-long/25' : 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-short/15 text-short border border-short/25';
        }
      }

      const eth = data.items.find(i => i.symbol === 'ETHUSDT');
      if (eth) {
        const avg = document.getElementById('card-eth-avg-rate');
        const apr = document.getElementById('card-eth-apr');
        const bin = document.getElementById('card-eth-binance');
        const byb = document.getElementById('card-eth-bybit');
        const bias = document.getElementById('card-eth-bias-pill');

        if (avg) {
          avg.innerText = `${eth.average_rate >= 0 ? '+' : ''}${eth.average_rate.toFixed(4)}%`;
          avg.className = eth.average_rate > 0.02 ? 'text-lg font-mono font-black text-amber-400' : 'text-lg font-mono font-black text-cyan-400';
        }
        if (apr) apr.innerText = `${eth.annualized_apr >= 0 ? '+' : ''}${eth.annualized_apr.toFixed(2)}%`;
        if (bin) bin.innerText = `${eth.binance_rate >= 0 ? '+' : ''}${eth.binance_rate.toFixed(4)}%`;
        if (byb) byb.innerText = `${eth.bybit_rate >= 0 ? '+' : ''}${eth.bybit_rate.toFixed(4)}%`;
        if (bias) {
          bias.innerText = eth.bias === 'LONGS_PAY' ? 'Longs pagan' : (eth.bias === 'SHORTS_PAY' ? 'Shorts pagan' : 'Neutral');
          bias.className = eth.bias === 'LONGS_PAY' ? 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-long/15 text-long border border-long/25' : 'px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-short/15 text-short border border-short/25';
        }
      }

      const biasEl = document.getElementById('global-market-bias');
      const avgFundingEl = document.getElementById('global-avg-funding');
      const overEl = document.getElementById('global-overheated-badge');
      if (biasEl) biasEl.innerText = data.market_bias;
      if (avgFundingEl) avgFundingEl.innerText = `${data.average_market_rate >= 0 ? '+' : ''}${data.average_market_rate.toFixed(4)}%`;
      if (overEl) overEl.innerText = `${data.overheated_longs_count + data.overheated_shorts_count} Pares en Alerta`;

      renderFundingTable();
    }

    function updateFundingClockUI() {
      const clock = document.getElementById('funding-countdown-clock');
      if (!clock) return;
      const h = Math.floor(fundingCountdownSec / 3600);
      const m = Math.floor((fundingCountdownSec % 3600) / 60);
      const s = fundingCountdownSec % 60;
      clock.innerText = `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function setFundingFilter(filter) {
      fundingFilter = filter;
      ['all', 'overheated', 'longs_pay', 'shorts_pay'].forEach(item => {
        const btn = document.getElementById(`btn-ff-${item}`);
        if (btn) {
          if (item === filter) {
            btn.className = 'px-2.5 py-1 rounded text-[11px] font-mono font-bold text-cyan-300 bg-surface-card border border-cyan-500/30 transition-all cursor-pointer';
          } else {
            btn.className = 'px-2.5 py-1 rounded text-[11px] font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer';
          }
        }
      });
      renderFundingTable();
    }

    function filterFundingTable() {
      renderFundingTable();
    }

    function renderFundingTable() {
      if (!fundingMatrixData || !fundingMatrixData.items) return;
      const tbody = document.getElementById('funding-table-body');
      const countDisplay = document.getElementById('funding-count-display');
      const search = (document.getElementById('funding-search-input')?.value || '').toUpperCase().trim();

      let items = [...fundingMatrixData.items];
      if (search) {
        items = items.filter(it => it.symbol.includes(search));
      }

      if (fundingFilter === 'overheated') {
        items = items.filter(it => it.thermal_state === 'OVERHEATED_LONG' || it.thermal_state === 'OVERHEATED_SHORT');
      } else if (fundingFilter === 'longs_pay') {
        items = items.filter(it => it.bias === 'LONGS_PAY');
      } else if (fundingFilter === 'shorts_pay') {
        items = items.filter(it => it.bias === 'SHORTS_PAY');
      }

      if (countDisplay) countDisplay.innerText = items.length;

      if (items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="py-8 text-center text-outline font-mono text-xs">No se encontraron pares que coincidan con el filtro actual.</td></tr>`;
        return;
      }

      tbody.innerHTML = items.map(item => {
        const isSelected = item.symbol === currentSymbol;
        const binFmt = `${item.binance_rate >= 0 ? '+' : ''}${item.binance_rate.toFixed(4)}%`;
        const bybFmt = `${item.bybit_rate >= 0 ? '+' : ''}${item.bybit_rate.toFixed(4)}%`;
        const avgFmt = `${item.average_rate >= 0 ? '+' : ''}${item.average_rate.toFixed(4)}%`;
        const aprFmt = `${item.annualized_apr >= 0 ? '+' : ''}${item.annualized_apr.toFixed(2)}%`;

        let thermalBadge = `<span class="px-2 py-0.5 rounded bg-surface border border-surface-border text-outline text-[10px] font-bold">Neutral</span>`;
        if (item.thermal_state === 'OVERHEATED_LONG') {
          thermalBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[10px] font-bold animate-pulse">🔥 Sobrecalentado</span>`;
        } else if (item.thermal_state === 'WARM_LONG') {
          thermalBadge = `<span class="px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 border border-cyan-500/25 text-[10px] font-bold">🟡 Moderado</span>`;
        } else if (item.thermal_state === 'OVERHEATED_SHORT') {
          thermalBadge = `<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30 text-[10px] font-bold animate-pulse">🧊 Pánico Short</span>`;
        }

        const biasBadge = item.bias === 'LONGS_PAY' 
          ? `<span class="text-long font-semibold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-long"></span>Longs pagan</span>`
          : (item.bias === 'SHORTS_PAY'
            ? `<span class="text-short font-semibold flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full bg-short"></span>Shorts pagan</span>`
            : `<span class="text-outline">Neutral</span>`);

        return `
          <tr class="${isSelected ? 'bg-mark/10 font-bold' : 'hover:bg-surface-panel/60'} transition-colors cursor-pointer" onclick="selectSymbol('${item.symbol}'); switchTab('mapa-de-calor');" title="Ver mapa de calor de ${item.symbol}">
            <td class="py-2.5 px-3 flex items-center gap-1.5">
              <span class="text-white font-bold">${item.symbol}</span>
              ${isSelected ? '<span class="w-1.5 h-1.5 rounded-full bg-mark"></span>' : ''}
            </td>
            <td class="py-2.5 px-3 text-white">$${item.mark_price.toLocaleString('en-US', { minimumFractionDigits: item.mark_price < 10 ? 4 : 2 })}</td>
            <td class="py-2.5 px-3 ${item.binance_rate >= 0 ? 'text-cyan-300' : 'text-purple-300'}">${binFmt}</td>
            <td class="py-2.5 px-3 ${item.bybit_rate >= 0 ? 'text-cyan-300' : 'text-purple-300'}">${bybFmt}</td>
            <td class="py-2.5 px-3 font-bold ${item.average_rate > 0.02 ? 'text-amber-400' : (item.average_rate >= 0 ? 'text-cyan-400' : 'text-purple-400')}">${avgFmt}</td>
            <td class="py-2.5 px-3 ${item.annualized_apr >= 0 ? 'text-white' : 'text-short'}">${aprFmt}</td>
            <td class="py-2.5 px-3">${biasBadge}</td>
            <td class="py-2.5 px-3 text-right">${thermalBadge}</td>
          </tr>
        `;
      }).join('');
    }

    // ==============================================================
    // SCREENER DE MERCADO & RADAR DE BALLENAS ENGINE
    // ==============================================================
    let screenerData = null;
    let screenerFilter = 'all'; // 'all', 'gainers', 'losers', 'oi_surge'
    let screenerSearchQuery = '';

    async function fetchScreenerData() {
      try {
        const resp = await fetch('/api/v1/screener');
        if (resp.ok) {
          const data = await resp.json();
          screenerData = data;
          renderScreenerUI(data);
        }
      } catch (err) {
        console.warn('Error al obtener datos del Screener:', err);
      }
    }

    function renderScreenerUI(data) {
      if (!data) return;

      // 1. Render Market Breadth
      if (data.breadth) {
        const b = data.breadth;
        const advEl = document.getElementById('screener-adv-pct');
        const decEl = document.getElementById('screener-dec-pct');
        const barAdv = document.getElementById('screener-bar-adv');
        const barDec = document.getElementById('screener-bar-dec');
        const oiEl = document.getElementById('screener-global-oi');
        const volEl = document.getElementById('screener-global-vol');

        if (advEl) advEl.innerText = `${b.advancers_pct}% (${b.advancers})`;
        if (decEl) decEl.innerText = `${b.decliners_pct}% (${b.decliners})`;
        if (barAdv) barAdv.style.width = `${b.advancers_pct}%`;
        if (barDec) barDec.style.width = `${b.decliners_pct}%`;
        if (oiEl) oiEl.innerText = `$${(b.total_market_oi_usd / 1e9).toFixed(2)}B`;
        if (volEl) volEl.innerText = `$${(b.total_market_vol_usd / 1e9).toFixed(2)}B`;
      }

      // 2. Render Hero Cards
      if (data.top_gainers && data.top_gainers.length > 0) {
        const g = data.top_gainers[0];
        const sym = document.getElementById('hero-gainer-sym');
        const pct = document.getElementById('hero-gainer-pct');
        const price = document.getElementById('hero-gainer-price');
        const oi = document.getElementById('hero-gainer-oi');

        if (sym) sym.innerText = g.symbol;
        if (pct) pct.innerText = `+${g.change_24h_pct.toFixed(2)}%`;
        if (price) price.innerText = `$${g.price.toLocaleString('en-US', { minimumFractionDigits: g.price < 10 ? 4 : 2 })}`;
        if (oi) oi.innerText = `OI: $${(g.open_interest_usd / 1e6).toFixed(1)}M`;
      }

      if (data.top_losers && data.top_losers.length > 0) {
        const l = data.top_losers[0];
        const sym = document.getElementById('hero-loser-sym');
        const pct = document.getElementById('hero-loser-pct');
        const price = document.getElementById('hero-loser-price');
        const oi = document.getElementById('hero-loser-oi');

        if (sym) sym.innerText = l.symbol;
        if (pct) pct.innerText = `${l.change_24h_pct.toFixed(2)}%`;
        if (price) price.innerText = `$${l.price.toLocaleString('en-US', { minimumFractionDigits: l.price < 10 ? 4 : 2 })}`;
        if (oi) oi.innerText = `OI: $${(l.open_interest_usd / 1e6).toFixed(1)}M`;
      }

      if (data.oi_surge && data.oi_surge.length > 0) {
        const w = data.oi_surge[0];
        const sym = document.getElementById('hero-whale-sym');
        const spike = document.getElementById('hero-whale-spike');
        const sig = document.getElementById('hero-whale-sig');
        const vol = document.getElementById('hero-whale-vol');

        if (sym) sym.innerText = w.symbol;
        if (spike) spike.innerText = `+${w.oi_change_pct.toFixed(1)}% OI`;
        if (sig) {
          sig.innerText = w.whale_signal === 'ACCUMULATION' ? '🐋 ACUMULACIÓN' : (w.whale_signal === 'DISTRIBUTION' ? '🐋 DISTRIBUCIÓN' : '⚡ SQUEEZE RISK');
          sig.className = w.whale_signal === 'DISTRIBUTION' ? 'px-1.5 py-0.5 rounded bg-short/20 text-short font-bold text-[9px] block' : 'px-1.5 py-0.5 rounded bg-yellow-400/20 text-yellow-300 font-bold text-[9px] block';
        }
        if (vol) vol.innerText = `Vol: $${(w.volume_24h_usd / 1e6).toFixed(1)}M`;
      }

      // 3. Render Table with Active Filter & Search
      renderScreenerTable();
    }

    function filterScreenerTab(category) {
      screenerFilter = category;
      ['all', 'gainers', 'losers', 'oi_surge'].forEach(cat => {
        const btn = document.getElementById(`sc-filter-${cat}`);
        if (btn) {
          if (cat === category) {
            btn.className = 'px-3 py-1.5 rounded-lg text-xs font-mono font-bold text-mark bg-surface-card border border-mark/30 transition-all cursor-pointer shadow-xs';
          } else {
            btn.className = 'px-3 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white bg-surface border border-surface-border flex items-center gap-1 transition-all cursor-pointer';
          }
        }
      });
      renderScreenerTable();
    }

    function handleScreenerSearch(query) {
      screenerSearchQuery = (query || '').trim().toUpperCase();
      renderScreenerTable();
    }

    function renderScreenerTable() {
      if (!screenerData) return;
      const tbody = document.getElementById('screener-table-body');
      if (!tbody) return;

      let list = [];
      if (screenerFilter === 'gainers') {
        list = screenerData.top_gainers || [];
      } else if (screenerFilter === 'losers') {
        list = screenerData.top_losers || [];
      } else if (screenerFilter === 'oi_surge') {
        list = screenerData.oi_surge || [];
      } else {
        list = screenerData.all_items || [];
      }

      if (screenerSearchQuery) {
        list = list.filter(item => item.symbol.toUpperCase().includes(screenerSearchQuery) || item.base_coin.toUpperCase().includes(screenerSearchQuery));
      }

      if (list.length === 0) {
        tbody.innerHTML = `
          <tr>
            <td colspan="10" class="py-8 text-center text-outline font-mono text-xs">
              No se encontraron pares coincidentes para los filtros seleccionados.
            </td>
          </tr>
        `;
        return;
      }

      tbody.innerHTML = list.map((item, idx) => {
        const isGainer = item.change_24h_pct >= 0;
        const chgBg = isGainer ? 'bg-long/10 text-long border-long/20' : 'bg-short/10 text-short border-short/20';

        let whaleBadge = '';
        if (item.whale_signal === 'ACCUMULATION') {
          whaleBadge = `<span class="px-2 py-0.5 rounded bg-yellow-400/15 text-yellow-300 border border-yellow-400/30 text-[9px] font-bold flex items-center gap-1 w-max"><span>🐋</span> Acumulación</span>`;
        } else if (item.whale_signal === 'DISTRIBUTION') {
          whaleBadge = `<span class="px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30 text-[9px] font-bold flex items-center gap-1 w-max"><span>🐋</span> Distribución</span>`;
        } else if (item.whale_signal === 'SQUEEZE_RISK') {
          whaleBadge = `<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30 text-[9px] font-bold animate-pulse flex items-center gap-1 w-max"><span>⚡</span> Squeeze Risk</span>`;
        } else if (item.oi_change_pct >= 5.0) {
          whaleBadge = `<span class="px-1.5 py-0.5 rounded bg-cyan-500/15 text-cyan-300 text-[9px] font-bold">+${item.oi_change_pct.toFixed(1)}%</span>`;
        } else {
          whaleBadge = `<span class="text-outline text-[10px] font-mono">Normal</span>`;
        }

        const volFmt = item.volume_24h_usd >= 1e9 ? `$${(item.volume_24h_usd / 1e9).toFixed(2)}B` : `$${(item.volume_24h_usd / 1e6).toFixed(1)}M`;
        const oiFmt = item.open_interest_usd >= 1e9 ? `$${(item.open_interest_usd / 1e9).toFixed(2)}B` : `$${(item.open_interest_usd / 1e6).toFixed(1)}M`;
        const fundFmt = `${item.funding_rate >= 0 ? '+' : ''}${item.funding_rate.toFixed(4)}%`;

        return `
          <tr class="hover:bg-surface-panel/60 transition-colors font-mono">
            <td class="py-2.5 px-3 text-outline text-[11px] font-bold">${idx + 1}</td>
            <td class="py-2.5 px-3">
              <div class="flex items-center gap-2">
                <span class="w-6 h-6 rounded-full bg-surface border border-surface-border flex items-center justify-center font-bold text-[10px] text-white">
                  ${item.base_coin.slice(0, 3)}
                </span>
                <div>
                  <span class="text-white font-bold text-xs block">${item.symbol}</span>
                  <span class="text-outline text-[9px]">${item.base_coin} Perp</span>
                </div>
              </div>
            </td>
            <td class="py-2.5 px-3 text-white font-bold">$${item.price.toLocaleString('en-US', { minimumFractionDigits: item.price < 10 ? 4 : 2 })}</td>
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded border text-[10px] font-bold ${chgBg}">
                ${isGainer ? '+' : ''}${item.change_24h_pct.toFixed(2)}%
              </span>
            </td>
            <td class="py-2.5 px-3 text-outline text-[11px]">
              $${item.low_24h.toLocaleString('en-US', { minimumFractionDigits: item.low_24h < 10 ? 3 : 1 })} - $${item.high_24h.toLocaleString('en-US', { minimumFractionDigits: item.high_24h < 10 ? 3 : 1 })}
            </td>
            <td class="py-2.5 px-3 text-cyan-400 font-bold">${oiFmt}</td>
            <td class="py-2.5 px-3">${whaleBadge}</td>
            <td class="py-2.5 px-3 text-white">${volFmt}</td>
            <td class="py-2.5 px-3 ${item.funding_rate >= 0 ? 'text-long' : 'text-short'}">${fundFmt}</td>
            <td class="py-2.5 px-3 text-right">
              <button onclick="analyzeSymbolFromScreener('${item.symbol}')" class="px-2.5 py-1 rounded bg-mark/10 hover:bg-mark/20 text-mark border border-mark/25 text-[10px] font-bold transition-all cursor-pointer inline-flex items-center gap-1 shadow-xs" title="Analizar ${item.symbol} en Mapa de Calor y TradingView">
                <span class="material-symbols-outlined text-[12px]">search</span>
                <span>Analizar</span>
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function analyzeSymbolFromScreener(symbol) {
      if (symbol === 'BTCUSDT' || symbol === 'ETHUSDT') {
        selectSymbol(symbol);
      } else {
        currentSymbol = symbol;
        const btcBtn = document.getElementById('btn-btc');
        const ethBtn = document.getElementById('btn-eth');
        if (btcBtn) btcBtn.className = 'px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer';
        if (ethBtn) ethBtn.className = 'px-2.5 sm:px-3 py-1 text-xs font-mono font-bold rounded text-on-surface-variant hover:text-white transition-all cursor-pointer';
        const badge = document.getElementById('hero-symbol-badge');
        if (badge) badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-yellow-400"></span>${symbol} USDⓈ-M`;
        fetchKlinesAndRender(symbol, tvTimeframe);
      }
      switchTab('mapa-de-calor');
    }

    // ==============================================================
    // TRACKER INSTITUCIONAL DE ETFS SPOT (BITCOIN & ETHEREUM) ENGINE
    // ==============================================================
    let etfTrackerData = null;
    let etfActiveAsset = 'BTC'; // 'BTC' o 'ETH'

    async function fetchEtfData() {
      try {
        const resp = await fetch('/api/v1/etfs');
        if (resp.ok) {
          const data = await resp.json();
          etfTrackerData = data;
          renderEtfUI(data);
        }
      } catch (err) {
        console.warn('Error al obtener datos institucionales de ETFs:', err);
      }
    }

    function switchEtfAsset(asset) {
      etfActiveAsset = asset;
      const btnBtc = document.getElementById('etf-btn-btc');
      const btnEth = document.getElementById('etf-btn-eth');

      if (asset === 'BTC') {
        if (btnBtc) btnBtc.className = 'px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold text-mark bg-surface-card border border-mark/30 transition-all cursor-pointer shadow-xs flex items-center gap-1.5';
        if (btnEth) btnEth.className = 'px-3.5 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer flex items-center gap-1.5';
      } else {
        if (btnBtc) btnBtc.className = 'px-3.5 py-1.5 rounded-lg text-xs font-mono font-semibold text-outline hover:text-white transition-all cursor-pointer flex items-center gap-1.5';
        if (btnEth) btnEth.className = 'px-3.5 py-1.5 rounded-lg text-xs font-mono font-bold text-cyan-400 bg-surface-card border border-cyan-400/30 transition-all cursor-pointer shadow-xs flex items-center gap-1.5';
      }

      if (etfTrackerData) {
        renderEtfUI(etfTrackerData);
      }
    }

    function renderEtfUI(data) {
      if (!data) return;

      const snap = etfActiveAsset === 'ETH' ? data.eth_etf : data.btc_etf;
      if (!snap) return;

      const coinSym = etfActiveAsset;

      // 1. Sentiment Badge
      const sentBadge = document.getElementById('etf-sentiment-badge');
      if (sentBadge) {
        if (snap.net_inflow_today_usd > 0) {
          sentBadge.className = 'px-2 py-0.5 rounded-full bg-emerald-400/10 text-emerald-300 font-mono text-[10px] font-bold border border-emerald-400/20 flex items-center gap-1';
          sentBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Inflow Institucional Positivo`;
        } else {
          sentBadge.className = 'px-2 py-0.5 rounded-full bg-red-400/10 text-red-300 font-mono text-[10px] font-bold border border-red-400/20 flex items-center gap-1';
          sentBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-red-400"></span> Outflow Neto / Redenciones`;
        }
      }

      // 2. Hero Cards
      const todayInflowEl = document.getElementById('etf-metric-today-inflow');
      const todayCoinsEl = document.getElementById('etf-metric-today-coins');
      const totalAumEl = document.getElementById('etf-metric-total-aum');
      const totalHoldingsEl = document.getElementById('etf-metric-total-holdings');
      const cumInflowEl = document.getElementById('etf-metric-cum-inflow');
      const leaderEl = document.getElementById('etf-metric-leader');
      const leaderShareEl = document.getElementById('etf-metric-leader-share');

      const isPos = snap.net_inflow_today_usd >= 0;
      const todayInflowM = (snap.net_inflow_today_usd / 1e6).toFixed(1);
      const coinPrice = snap.total_crypto_holdings > 0 ? (snap.total_aum_usd / snap.total_crypto_holdings) : 75000;
      const todayCoinsApprox = Math.round(snap.net_inflow_today_usd / coinPrice);

      if (todayInflowEl) {
        todayInflowEl.className = `text-xl font-bold font-mono block ${isPos ? 'text-long' : 'text-short'}`;
        todayInflowEl.innerText = `${isPos ? '+' : ''}$${todayInflowM}M USD`;
      }
      if (todayCoinsEl) {
        todayCoinsEl.innerText = `~${Math.abs(todayCoinsApprox).toLocaleString('en-US')} ${coinSym} ${isPos ? 'absorbidos' : 'liquidados'}`;
      }

      if (totalAumEl) {
        totalAumEl.innerText = `$${(snap.total_aum_usd / 1e9).toFixed(2)}B USD`;
      }
      if (totalHoldingsEl) {
        totalHoldingsEl.innerText = `${snap.total_crypto_holdings.toLocaleString('en-US', { maximumFractionDigits: 0 })} ${coinSym} en custodia`;
      }

      if (cumInflowEl) {
        const cumM = (snap.cumulative_inflow_usd / 1e9).toFixed(2);
        cumInflowEl.innerText = `${snap.cumulative_inflow_usd >= 0 ? '+' : ''}$${cumM}B USD`;
      }

      if (leaderEl) {
        leaderEl.innerText = snap.dominant_fund;
      }
      if (leaderShareEl) {
        const topFund = snap.funds[0];
        const share = topFund && snap.total_aum_usd > 0 ? ((topFund.aum_usd / snap.total_aum_usd) * 100).toFixed(1) : '49.6';
        leaderShareEl.innerText = `${share}% cuota de mercado institucional`;
      }

      // 3. Render Inflows Historical Bar Chart
      renderEtfHistoryBars(snap.daily_history);

      // 4. Render Table
      renderEtfTable(snap.funds);
    }

    function renderEtfHistoryBars(history) {
      const container = document.getElementById('etf-bars-container');
      if (!container || !history || history.length === 0) return;

      const maxVal = Math.max(...history.map(h => Math.abs(h.net_inflow_usd)), 100_000_000.0);

      container.innerHTML = history.map((day, idx) => {
        const isPos = day.net_inflow_usd >= 0;
        const valM = (day.net_inflow_usd / 1e6).toFixed(1);
        const absVal = Math.abs(day.net_inflow_usd);
        const barHeightPct = Math.min(100, Math.max(14, Math.round((absVal / maxVal) * 95)));
        const colorClass = isPos ? 'bg-long hover:bg-long/80 shadow-[0_0_10px_rgba(0,240,144,0.3)]' : 'bg-short hover:bg-short/80 shadow-[0_0_10px_rgba(255,51,88,0.3)]';
        const dateShort = day.date.slice(5); // MM-DD

        return `
          <div class="flex-1 flex flex-col items-center justify-end h-full group relative cursor-pointer min-w-[36px]">
            <!-- Tooltip Hover Card -->
            <div class="absolute -top-11 z-30 hidden group-hover:flex flex-col items-center bg-[#07090e] border border-surface-border px-2 py-1 rounded text-[10px] font-mono shadow-xl pointer-events-none whitespace-nowrap">
              <span class="text-white font-bold">${day.date}</span>
              <span class="${isPos ? 'text-long' : 'text-short'} font-bold">${isPos ? '+' : ''}$${valM}M USD (${day.top_inflow_ticker})</span>
            </div>

            <!-- Value Top Label -->
            <span class="text-[9px] font-mono font-bold ${isPos ? 'text-long' : 'text-short'} mb-1 hidden sm:block">
              ${isPos ? '+' : ''}${valM}M
            </span>

            <!-- Colored Bar -->
            <div class="w-full max-w-[28px] rounded-t-sm transition-all duration-300 ${colorClass}" style="height: ${barHeightPct}%;"></div>

            <!-- Date Bottom Label -->
            <span class="text-[9px] font-mono text-outline mt-1.5">${dateShort}</span>
          </div>
        `;
      }).join('');
    }

    function renderEtfTable(funds) {
      const tbody = document.getElementById('etf-table-body');
      if (!tbody || !funds) return;

      tbody.innerHTML = funds.map((f, idx) => {
        const isPos = f.net_inflow_today_usd >= 0;
        const aumFmt = f.aum_usd >= 1e9 ? `$${(f.aum_usd / 1e9).toFixed(2)}B` : `$${(f.aum_usd / 1e6).toFixed(1)}M`;
        const todayFmt = f.net_inflow_today_usd === 0 ? '$0.0M' : `${isPos ? '+' : ''}$${(f.net_inflow_today_usd / 1e6).toFixed(1)}M`;
        const cumFmt = `${f.cumulative_inflow_usd >= 0 ? '+' : ''}$${(f.cumulative_inflow_usd / 1e9).toFixed(2)}B`;
        const todayColor = f.net_inflow_today_usd > 0 ? 'text-long' : (f.net_inflow_today_usd < 0 ? 'text-short' : 'text-outline');
        const cumColor = f.cumulative_inflow_usd >= 0 ? 'text-white' : 'text-short';

        return `
          <tr class="hover:bg-surface-panel/60 transition-colors">
            <td class="py-2.5 px-3">
              <span class="px-2 py-0.5 rounded bg-surface border border-surface-border text-white font-bold text-xs">${f.ticker}</span>
            </td>
            <td class="py-2.5 px-3 text-white font-semibold">${f.issuer}</td>
            <td class="py-2.5 px-3 text-outline text-[11px]">${f.name}</td>
            <td class="py-2.5 px-3 text-white font-bold">${aumFmt}</td>
            <td class="py-2.5 px-3 text-cyan-400 font-bold">${f.crypto_holdings.toLocaleString('en-US', { maximumFractionDigits: 0 })} ${etfActiveAsset}</td>
            <td class="py-2.5 px-3 ${todayColor} font-bold">${todayFmt}</td>
            <td class="py-2.5 px-3 ${cumColor} font-bold">${cumFmt}</td>
            <td class="py-2.5 px-3 text-outline">${f.fee_pct.toFixed(2)}%</td>
            <td class="py-2.5 px-3 text-right text-outline text-[11px]">${f.custodian}</td>
          </tr>
        `;
      }).join('');
    }

    // Check hash for direct tab linking (e.g. #manual)
    if (window.location.hash === '#manual') {
      switchTab('manual');
    }

    // Initial Start
    updateAudioUI();
    updateNotifUI();
    initTelegramUI();
    initRektAudioUI();
    initRektWebSocket();
    fetchRecentLiquidations();
    fetchHeatmap(true);
    fetchFundingRates();
    setInterval(fetchFundingRates, 30000);
    fetchScreenerData();
    setInterval(() => {
      const active = document.getElementById('tab-screener');
      if (active && !active.classList.contains('hidden')) {
        fetchScreenerData();
      }
    }, 20000);
    fetchEtfData();
    setInterval(() => {
      const active = document.getElementById('tab-etfs');
      if (active && !active.classList.contains('hidden')) {
        fetchEtfData();
      }
    }, 30000);
    startAutoRefreshTimer();
    recalcSimulator();
    initTradingViewChart();
    setViewMode('tv');
  </script>

</body>
</html>
"""


def get_dashboard_html() -> str:
    """Retorna el contenido HTML del visualizador de mapa de calor interactivo."""
    return DASHBOARD_HTML
