@echo off
title LiqScope - Visual Liquidation Heatmap
echo ======================================================================
echo                LiqScope - Visual Liquidation Heatmap
echo ======================================================================
echo Abriendo el navegador en http://localhost:8000 ...
start "" "http://localhost:8000"
echo Iniciando servidor FastAPI en http://127.0.0.1:8000 ...
py -3.12 -m uvicorn liqscope.api.app:create_app --factory --host 127.0.0.1 --port 8000
pause
