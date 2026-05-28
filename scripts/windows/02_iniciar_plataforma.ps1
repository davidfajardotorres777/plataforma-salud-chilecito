$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: inicio Windows =="

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose up -d
} else {
    Write-Host "Docker no esta disponible. La interfaz web funcionara en modo demo JSON."
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "Preparando Oracle automaticamente..."
    try {
        .\.venv\Scripts\python.exe scripts\setup_oracle.py
    } catch {
        Write-Host "No se pudo preparar Oracle automaticamente. La web se inicia igual en modo demo JSON."
        Write-Host $_
    }
}

Start-Process "http://localhost:8000"
.\.venv\Scripts\python.exe -m src.webapp.server
