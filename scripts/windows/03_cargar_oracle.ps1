$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: carga Oracle Windows =="
Write-Host "Este paso es automatico y prepara toda la base Oracle."

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno virtual." }
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias." }

.\.venv\Scripts\python.exe scripts\setup_oracle.py
if ($LASTEXITCODE -ne 0) { throw "No se pudo cargar la base Oracle. Revisa el mensaje anterior." }

Write-Host "Base Oracle cargada automaticamente."
