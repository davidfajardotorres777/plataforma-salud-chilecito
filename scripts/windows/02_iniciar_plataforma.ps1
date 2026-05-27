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

Start-Process "http://localhost:8000"
.\.venv\Scripts\python.exe -m src.webapp.server
