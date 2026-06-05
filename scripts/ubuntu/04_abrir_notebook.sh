#!/usr/bin/env bash
set -euo pipefail

echo "== Salud Chilecito: notebook Ubuntu =="

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
pip install -r requirements.txt

echo "Abriendo notebook desde la raiz del repositorio..."
python -m notebook --notebook-dir=. notebooks/SaludChilecito_DAO_Demo.ipynb
