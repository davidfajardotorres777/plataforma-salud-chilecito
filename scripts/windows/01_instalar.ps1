$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: instalacion Windows =="
Write-Host "Links oficiales:"
Write-Host "- Git for Windows: https://gitforwindows.org/"
Write-Host "- Python 3.12+: https://www.python.org/downloads/windows/"
Write-Host "- Docker Desktop: https://www.docker.com/products/docker-desktop/"
Write-Host "- SQL Developer: https://www.oracle.com/database/sqldeveloper/"

function Test-Command($name) {
    return [bool](Get-Command $name -ErrorAction SilentlyContinue)
}

if (-not (Test-Command git)) {
    Write-Host "Instalando Git con winget..."
    winget install --id Git.Git -e --source winget
}

if (-not (Test-Command python)) {
    Write-Host "Instalando Python 3 con winget..."
    winget install --id Python.Python.3.12 -e --source winget
}

if (-not (Test-Command docker)) {
    Write-Host "Instalando Docker Desktop con winget..."
    winget install --id Docker.DockerDesktop -e --source winget
    Write-Host "Reinicia Windows o abre Docker Desktop antes de continuar."
}

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -r requirements.txt

Write-Host "Instalacion completada."
Write-Host "Siguiente paso: scripts\windows\02_iniciar_plataforma.ps1"
