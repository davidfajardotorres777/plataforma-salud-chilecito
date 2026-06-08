$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: notebook Windows =="

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno virtual." }
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias." }

$NotebookUrl = "http://127.0.0.1:8888/notebooks/notebooks/SaludChilecito_DAO_Demo.ipynb"
$Args = @(
    "-m", "notebook",
    "--notebook-dir=.",
    "--no-browser",
    "--port=8888",
    "--ServerApp.ip=127.0.0.1",
    "--ServerApp.token=",
    "--ServerApp.password="
)

Write-Host "Iniciando Jupyter en http://127.0.0.1:8888 ..."
Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList $Args -WorkingDirectory (Get-Location)
Start-Sleep -Seconds 5

Write-Host "Abriendo notebook: $NotebookUrl"
Start-Process $NotebookUrl
