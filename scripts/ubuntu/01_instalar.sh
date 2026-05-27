#!/usr/bin/env bash
set -euo pipefail

echo "== Salud Chilecito: instalacion Ubuntu =="

sudo apt update
sudo apt install -y git python3 python3-venv python3-pip docker.io docker-compose-plugin

if ! groups "$USER" | grep -q docker; then
  sudo usermod -aG docker "$USER"
  echo "Tu usuario fue agregado al grupo docker. Cierra sesion y vuelve a entrar antes de usar Docker sin sudo."
fi

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo "Instalacion completada."
echo "Siguiente paso: bash scripts/ubuntu/02_iniciar_plataforma.sh"
