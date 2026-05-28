#!/usr/bin/env bash
set -euo pipefail

echo "== Salud Chilecito: carga Oracle Ubuntu =="
echo "Este paso es automatico. No requiere SQL Developer ni SQL*Plus."

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements.txt
python scripts/setup_oracle.py

echo "Base Oracle cargada automaticamente."
