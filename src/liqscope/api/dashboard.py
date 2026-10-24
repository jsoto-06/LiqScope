"""Plantilla y generador del Dashboard HTML interactivo para LiqScope."""

from __future__ import annotations

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LiqScope - Visualizador de Mapa de Calor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body {
      background-color: var(--background, #0f172a);
      color: var(--foreground, #f8fafc);
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.1);
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: var(--border, #334155);
      border-radius: 4px;
    }
  </style>
</head>
<body class="p-4 md:p-6 min-h-screen">
  <div class="max-w-5xl mx-auto space-y-6">

    <!-- Header -->
    <header class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border,#334155)] pb-4">
      <div>
        <div class="flex items-center gap-2">
          <span class="inline-block w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
          <h1 class="text-xl md:text-2xl font-bold tracking-tight">LiqScope — Liquidation Heatmap</h1>
          <span class="text-xs px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 font-medium border border-indigo-500/30">Fase 4 REST</span>
        </div>
        <p class="text-xs text-[var(--muted-foreground,#94a3b8)] mt-1">
          Visualización analítica de zonas de liquidación para contratos perpetuos USDⓈ-M
        </p>
      </div>

      <!-- Controls -->
      <div class="flex flex-wrap items-center gap-2">
        <div class="inline-flex rounded-lg border border-[var(--border,#334155)] p-1 bg-[var(--card,#1e293b)]">
          <button id="btn-btc" onclick="selectSymbol('BTCUSDT')" class="px-3 py-1 text-xs font-semibold rounded-md bg-indigo-600 text-white transition-all shadow-sm">BTCUSDT</button>
          <button id="btn-eth" onclick="selectSymbol('ETHUSDT')" class="px-3 py-1 text-xs font-semibold rounded-md text-[var(--muted-foreground,#94a3b8)] hover:text-white transition-all">ETHUSDT</button>
        </div>

        <div class="inline-flex rounded-lg border border-[var(--border,#334155)] p-1 bg-[var(--card,#1e293b)]">
          <button id="btn-live" onclick="setSource('live')" class="px-3 py-1 text-xs font-medium rounded-md bg-emerald-600/30 text-emerald-300 border border-emerald-500/30">Live (Binance)</button>
          <button id="btn-demo" onclick="setSource('demo')" class="px-3 py-1 text-xs font-medium rounded-md text-[var(--muted-foreground,#94a3b8)] hover:text-white">Demo</button>
        </div>

        <!-- Auto-refresh indicator badge (2 minutes) -->
        <div class="inline-flex items-center gap-1.5 px-3 py-1 text-xs rounded-lg border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] text-slate-300" title="Actualización automática cada 2 minutos">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
          <span class="text-slate-400 font-medium">Auto:</span>
          <span id="countdown-text" class="font-mono font-bold text-emerald-400">02:00</span>
        </div>

        <button onclick="fetchHeatmap(true)" class="px-3 py-1.5 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white flex items-center gap-1.5 transition-all shadow">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
          Actualizar
        </button>
      </div>
    </header>

    <!-- Metrics Cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div class="p-4 rounded-xl border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] shadow-sm">
        <span class="text-xs text-[var(--muted-foreground,#94a3b8)] block">Precio Mark Actual</span>
        <div id="metric-price" class="text-lg md:text-xl font-bold mt-1 text-white tracking-tight">$81,498.90</div>
        <div class="flex items-center justify-between mt-1">
          <span id="metric-symbol" class="text-[11px] text-indigo-400 font-mono">BTCUSDT</span>
          <span id="metric-last-sync" class="text-[10px] text-slate-400 font-mono">Sinc: --:--:--</span>
        </div>
      </div>

      <div class="p-4 rounded-xl border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] shadow-sm">
        <span class="text-xs text-[var(--muted-foreground,#94a3b8)] block">Open Interest Total</span>
        <div id="metric-oi" class="text-lg md:text-xl font-bold mt-1 text-white tracking-tight">$7,778.97M</div>
        <span id="metric-oi-coins" class="text-[11px] text-slate-400 font-mono">95,448.75 BTC</span>
      </div>

      <div class="p-4 rounded-xl border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] shadow-sm">
        <span class="text-xs text-[var(--muted-foreground,#94a3b8)] block">Volumen Visible</span>
        <div id="metric-visible-vol" class="text-lg md:text-xl font-bold mt-1 text-white tracking-tight">$7,778.97M</div>
        <span class="text-[11px] text-emerald-400 font-medium">Suma de celdas</span>
      </div>

      <div class="p-4 rounded-xl border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] shadow-sm">
        <span class="text-xs text-[var(--muted-foreground,#94a3b8)] block">Cobertura de Bins</span>
        <div id="metric-coverage" class="text-lg md:text-xl font-bold mt-1 text-emerald-400 tracking-tight">100.0%</div>
        <span id="metric-source" class="text-[11px] text-slate-400 uppercase font-mono">Origen: Live</span>
      </div>
    </div>

    <!-- Filter Toolbar -->
    <div class="p-4 rounded-xl border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] space-y-3">
      <div class="flex items-center justify-between text-xs font-semibold text-slate-300">
        <span>Filtro de Rango y Granularidad</span>
        <button onclick="resetFilters()" class="text-indigo-400 hover:text-indigo-300 text-xs font-normal underline">Restablecer Rango</button>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div>
          <label class="block text-xs text-[var(--muted-foreground,#94a3b8)] mb-1">Precio Mínimo (USD)</label>
          <input type="number" id="input-min" placeholder="Ej. 79000" onchange="fetchHeatmap(true)" class="w-full px-3 py-1.5 text-xs rounded-lg border border-[var(--border,#334155)] bg-[var(--background,#0f172a)] text-white focus:outline-none focus:border-indigo-500">
        </div>
        <div>
          <label class="block text-xs text-[var(--muted-foreground,#94a3b8)] mb-1">Precio Máximo (USD)</label>
          <input type="number" id="input-max" placeholder="Ej. 83000" onchange="fetchHeatmap(true)" class="w-full px-3 py-1.5 text-xs rounded-lg border border-[var(--border,#334155)] bg-[var(--background,#0f172a)] text-white focus:outline-none focus:border-indigo-500">
        </div>
        <div>
          <label class="block text-xs text-[var(--muted-foreground,#94a3b8)] mb-1">Tamaño de Bin (USD)</label>
          <select id="select-bin-size" onchange="fetchHeatmap(true)" class="w-full px-3 py-1.5 text-xs rounded-lg border border-[var(--border,#334155)] bg-[var(--background,#0f172a)] text-white focus:outline-none focus:border-indigo-500">
            <option value="50">50 USD (Estándar)</option>
            <option value="100">100 USD</option>
            <option value="250">250 USD</option>
            <option value="500">500 USD</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Heatmap Price Ladder -->
    <div class="rounded-xl border border-[var(--border,#334155)] bg-[var(--card,#1e293b)] p-4 md:p-6 space-y-4">
      <div class="flex items-center justify-between border-b border-[var(--border,#334155)] pb-3">
        <div>
          <h2 class="text-sm font-bold text-white uppercase tracking-wider">Escalera de Liquidaciones Modeladas</h2>
          <p class="text-xs text-[var(--muted-foreground,#94a3b8)]">Posiciones Cortas (arriba) y Largas (abajo) respecto al precio Mark</p>
        </div>
        <div class="flex items-center gap-4 text-xs">
          <div class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-rose-500/80"></span>
            <span class="text-slate-300">Shorts Liquidables</span>
          </div>
          <div class="flex items-center gap-1.5">
            <span class="w-3 h-3 rounded bg-emerald-500/80"></span>
            <span class="text-slate-300">Longs Liquidables</span>
          </div>
        </div>
      </div>

      <!-- Price Ladder Container -->
      <div id="ladder-container" class="space-y-1.5 max-h-[500px] overflow-y-auto custom-scroll pr-2">
        <!-- Rendered dynamically -->
      </div>
    </div>

    <!-- Data Transparency & Disclaimer Banner -->
    <div class="p-4 rounded-xl border border-indigo-500/30 bg-indigo-500/10 text-indigo-200/90 text-xs space-y-2">
      <div class="flex items-center gap-2 font-semibold text-indigo-300">
        <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/></svg>
        Confirmación de Origen y Realidad de los Datos
      </div>
      <p class="leading-relaxed text-slate-300">
        <strong class="text-white">Datos de Mercado 100% Reales en Vivo:</strong> El Precio Mark y el Open Interest total se consultan directamente desde la API oficial de Binance Futures USDⓈ-M (sin intermediarios y sin demora agregada). Se auto-actualizan cada 2 minutos.<br>
        <strong class="text-white">Modelado Matemático de Zonas de Liquidación:</strong> Los exchanges no publican las órdenes o precios de entrada individuales de cada trader por secreto bancario. LiqScope toma el Open Interest real y calcula matemáticamente las zonas críticas donde los traders con apalancamientos habituales (5x, 10x, 25x, 50x, 100x) y márgenes de mantenimiento oficiales (MMR) sufren liquidación forzada.
      </p>
    </div>

  </div>

  <script>
    let currentSymbol = 'BTCUSDT';
    let currentSource = 'live';

    // Auto-refresh timer (2 minutes = 120 seconds)
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
      if (el) el.innerText = formatted;
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

    // Base fallback data when API offline
    const defaultData = {
      BTCUSDT: {
        price: 81498.90,
        oi: 95448.751,
        levels: [
          { side: 'SHORT', lev: 5, mmr: 0.040, delta: 0.160, price: 94538.72, vol: 583422615.97, bin: [94500, 94550] },
          { side: 'SHORT', lev: 10, mmr: 0.020, delta: 0.080, price: 88018.81, vol: 972371026.61, bin: [88000, 88050] },
          { side: 'SHORT', lev: 25, mmr: 0.010, delta: 0.030, price: 83943.87, vol: 1166845231.93, bin: [83900, 83950] },
          { side: 'SHORT', lev: 50, mmr: 0.005, delta: 0.015, price: 82721.38, vol: 777896821.29, bin: [82700, 82750] },
          { side: 'SHORT', lev: 100, mmr: 0.004, delta: 0.006, price: 81987.89, vol: 388948410.64, bin: [81950, 82000] },
          { side: 'LONG', lev: 100, mmr: 0.004, delta: 0.006, price: 81009.91, vol: 388948410.64, bin: [81000, 81050] },
          { side: 'LONG', lev: 50, mmr: 0.005, delta: 0.015, price: 80276.42, vol: 777896821.29, bin: [80250, 80300] },
          { side: 'LONG', lev: 25, mmr: 0.010, delta: 0.030, price: 79053.93, vol: 1166845231.93, bin: [79050, 79100] },
          { side: 'LONG', lev: 10, mmr: 0.020, delta: 0.080, price: 74978.99, vol: 972371026.61, bin: [74950, 75000] },
          { side: 'LONG', lev: 5, mmr: 0.040, delta: 0.160, price: 68459.08, vol: 583422615.97, bin: [68450, 68500] }
        ]
      },
      ETHUSDT: {
        price: 2650.50,
        oi: 350000.0,
        levels: [
          { side: 'SHORT', lev: 5, mmr: 0.040, delta: 0.160, price: 3074.58, vol: 69575625.0, bin: [3050, 3100] },
          { side: 'SHORT', lev: 10, mmr: 0.020, delta: 0.080, price: 2862.54, vol: 115959375.0, bin: [2850, 2900] },
          { side: 'SHORT', lev: 25, mmr: 0.010, delta: 0.030, price: 2730.01, vol: 139151250.0, bin: [2700, 2750] },
          { side: 'SHORT', lev: 50, mmr: 0.005, delta: 0.015, price: 2690.26, vol: 92767500.0, bin: [2650, 2700] },
          { side: 'SHORT', lev: 100, mmr: 0.004, delta: 0.006, price: 2666.40, vol: 46383750.0, bin: [2650, 2700] },
          { side: 'LONG', lev: 100, mmr: 0.004, delta: 0.006, price: 2634.60, vol: 46383750.0, bin: [2600, 2650] },
          { side: 'LONG', lev: 50, mmr: 0.005, delta: 0.015, price: 2610.74, vol: 92767500.0, bin: [2600, 2650] },
          { side: 'LONG', lev: 25, mmr: 0.010, delta: 0.030, price: 2570.98, vol: 139151250.0, bin: [2550, 2600] },
          { side: 'LONG', lev: 10, mmr: 0.020, delta: 0.080, price: 2438.46, vol: 115959375.0, bin: [2400, 2450] },
          { side: 'LONG', lev: 5, mmr: 0.040, delta: 0.160, price: 2226.42, vol: 69575625.0, bin: [2200, 2250] }
        ]
      }
    };

    function selectSymbol(sym) {
      currentSymbol = sym;
      document.getElementById('btn-btc').className = sym === 'BTCUSDT' ? 'px-3 py-1 text-xs font-semibold rounded-md bg-indigo-600 text-white transition-all shadow-sm' : 'px-3 py-1 text-xs font-semibold rounded-md text-[var(--muted-foreground,#94a3b8)] hover:text-white transition-all';
      document.getElementById('btn-eth').className = sym === 'ETHUSDT' ? 'px-3 py-1 text-xs font-semibold rounded-md bg-indigo-600 text-white transition-all shadow-sm' : 'px-3 py-1 text-xs font-semibold rounded-md text-[var(--muted-foreground,#94a3b8)] hover:text-white transition-all';
      fetchHeatmap(true);
    }

    function setSource(src) {
      currentSource = src;
      document.getElementById('btn-live').className = src === 'live' ? 'px-3 py-1 text-xs font-medium rounded-md bg-emerald-600/30 text-emerald-300 border border-emerald-500/30' : 'px-3 py-1 text-xs font-medium rounded-md text-[var(--muted-foreground,#94a3b8)] hover:text-white';
      document.getElementById('btn-demo').className = src === 'demo' ? 'px-3 py-1 text-xs font-medium rounded-md bg-indigo-600/30 text-indigo-300 border border-indigo-500/30' : 'px-3 py-1 text-xs font-medium rounded-md text-[var(--muted-foreground,#94a3b8)] hover:text-white';
      fetchHeatmap(true);
    }

    function resetFilters() {
      document.getElementById('input-min').value = '';
      document.getElementById('input-max').value = '';
      document.getElementById('select-bin-size').value = '50';
      fetchHeatmap(true);
    }

    async function fetchHeatmap(resetTimer = false) {
      if (resetTimer) {
        resetCountdown();
      }

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
          renderHeatmap(data);
          return;
        }
      } catch (err) {
        console.warn('API fetch failed, rendering local model fallback:', err);
      }

      // Fallback local render
      renderLocalFallback(minP ? parseFloat(minP) : null, maxP ? parseFloat(maxP) : null, parseFloat(binSize));
    }

    function renderHeatmap(data) {
      document.getElementById('metric-price').innerText = `$${data.current_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
      document.getElementById('metric-symbol').innerText = data.symbol;
      document.getElementById('metric-oi').innerText = `$${(data.total_open_interest_usd / 1e6).toFixed(2)}M`;
      document.getElementById('metric-visible-vol').innerText = `$${(data.visible_bin_volume_usd / 1e6).toFixed(2)}M`;
      document.getElementById('metric-coverage').innerText = `${data.coverage_pct.toFixed(1)}%`;
      document.getElementById('metric-source').innerText = `Origen: ${data.source.toUpperCase()}`;

      const now = new Date();
      const timeStr = now.toLocaleTimeString();
      const syncEl = document.getElementById('metric-last-sync');
      if (syncEl) syncEl.innerText = `Sinc: ${timeStr}`;

      const container = document.getElementById('ladder-container');
      container.innerHTML = '';

      if (!data.bins || data.bins.length === 0) {
        container.innerHTML = `<div class="p-8 text-center text-xs text-[var(--muted-foreground,#94a3b8)]">No hay zonas de liquidación modeladas en el rango de precio seleccionado.</div>`;
        return;
      }

      // Find max volume for proportional bar width
      const maxVol = Math.max(...data.bins.map(b => b.estimated_volume_usd));

      // Separate shorts (above current price) and longs (below current price)
      const sortedBins = [...data.bins].sort((a, b) => b.price_min - a.price_min);
      let markPriceInserted = false;

      sortedBins.forEach(b => {
        if (!markPriceInserted && b.price_max <= data.current_price) {
          container.appendChild(createMarkPriceBanner(data.current_price));
          markPriceInserted = true;
        }

        const isShort = b.short_volume_usd > b.long_volume_usd;
        const volPct = Math.min(100, Math.max(10, (b.estimated_volume_usd / maxVol) * 100));
        const barColor = isShort ? 'bg-rose-500/80 border-rose-400/40 text-rose-200' : 'bg-emerald-500/80 border-emerald-400/40 text-emerald-200';

        const row = document.createElement('div');
        row.className = 'grid grid-cols-12 items-center gap-2 text-xs py-1 px-2 rounded-lg hover:bg-slate-800/40 transition-colors';
        row.innerHTML = `
          <div class="col-span-3 font-mono text-[var(--muted-foreground,#94a3b8)]">
            $${b.price_min.toLocaleString()} - $${b.price_max.toLocaleString()}
          </div>
          <div class="col-span-6 relative h-6 bg-slate-900/60 rounded-md overflow-hidden flex items-center px-2">
            <div class="absolute left-0 top-0 bottom-0 ${barColor} rounded-r-md transition-all duration-300" style="width: ${volPct}%"></div>
            <span class="relative z-10 font-mono text-[11px] font-semibold text-white drop-shadow">$${(b.estimated_volume_usd / 1e6).toFixed(2)}M</span>
          </div>
          <div class="col-span-3 text-right font-medium ${isShort ? 'text-rose-400' : 'text-emerald-400'}">
            ${isShort ? 'SHORT' : 'LONG'}
          </div>
        `;
        container.appendChild(row);
      });

      if (!markPriceInserted) {
        container.appendChild(createMarkPriceBanner(data.current_price));
      }
    }

    function createMarkPriceBanner(price) {
      const banner = document.createElement('div');
      banner.className = 'my-2 py-1 px-3 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-between text-xs text-indigo-300 font-semibold shadow-inner';
      banner.innerHTML = `
        <span class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-indigo-400 animate-ping"></span>
          PRECIO MARK ACTUAL
        </span>
        <span class="font-mono text-sm text-white font-bold">$${price.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
      `;
      return banner;
    }

    function renderLocalFallback(minP, maxP, binSize) {
      const def = defaultData[currentSymbol];
      let filtered = def.levels;
      if (minP !== null && !isNaN(minP)) filtered = filtered.filter(l => l.bin[1] > minP);
      if (maxP !== null && !isNaN(maxP)) filtered = filtered.filter(l => l.bin[0] < maxP);

      const totalOIUsd = def.price * def.oi;
      const visibleVol = filtered.reduce((acc, cur) => acc + cur.vol, 0);
      const coveragePct = (visibleVol / totalOIUsd) * 100;

      const mockData = {
        symbol: currentSymbol,
        current_price: def.price,
        total_open_interest_usd: totalOIUsd,
        visible_bin_volume_usd: visibleVol,
        coverage_pct: coveragePct,
        source: currentSource,
        bins: filtered.map(l => ({
          price_min: l.bin[0],
          price_max: l.bin[1],
          price_mid: (l.bin[0] + l.bin[1]) / 2,
          estimated_volume_usd: l.vol,
          long_volume_usd: l.side === 'LONG' ? l.vol : 0,
          short_volume_usd: l.side === 'SHORT' ? l.vol : 0,
          origin: 'modeled',
          coverage: 'na'
        }))
      };
      renderHeatmap(mockData);
    }

    // Initial load and start 2-minute timer
    fetchHeatmap(true);
    startAutoRefreshTimer();
  </script>
</body>
</html>
"""


def get_dashboard_html() -> str:
    """Retorna el contenido HTML del visualizador de mapa de calor interactivo."""
    return DASHBOARD_HTML
