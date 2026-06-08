#!/usr/bin/env bash
set -euo pipefail

echo "== Salud Chilecito: notebook Ubuntu =="

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements.txt

mkdir -p runtime

NOTEBOOK_URL="http://127.0.0.1:8888/notebooks/notebooks/SaludChilecito_DAO_Demo.ipynb"

echo "Iniciando Jupyter en http://127.0.0.1:8888 ..."
nohup python -m notebook \
  --notebook-dir=. \
  --no-browser \
  --port=8888 \
  --ServerApp.ip=127.0.0.1 \
  --ServerApp.token= \
  --ServerApp.password= \
  > runtime/jupyter_salud.log 2>&1 &

sleep 5

echo "Abriendo notebook: $NOTEBOOK_URL"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$NOTEBOOK_URL" >/dev/null 2>&1 || true
else
  echo "$NOTEBOOK_URL"
fi
