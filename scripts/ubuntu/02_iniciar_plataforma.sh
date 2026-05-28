#!/usr/bin/env bash
set -euo pipefail

echo "== Salud Chilecito: inicio Ubuntu =="

if [ ! -f .env ]; then
  cp .env.example .env
fi

if command -v docker >/dev/null 2>&1; then
  docker compose up -d || sudo docker compose up -d
else
  echo "Docker no esta disponible. La interfaz web funcionara en modo demo JSON."
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements.txt

if command -v docker >/dev/null 2>&1; then
  echo "Preparando Oracle automaticamente..."
  python scripts/setup_oracle.py || echo "No se pudo preparar Oracle automaticamente. La web se inicia igual en modo demo JSON."
fi

if command -v xdg-open >/dev/null 2>&1; then
  xdg-open http://localhost:8000 >/dev/null 2>&1 || true
fi

python -m src.webapp.server
