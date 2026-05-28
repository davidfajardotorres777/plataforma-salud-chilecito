$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: carga Oracle Windows =="
Write-Host "Este paso es automatico. No requiere SQL Developer ni SQL*Plus."

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_oracle.py

Write-Host "Base Oracle cargada automaticamente."
