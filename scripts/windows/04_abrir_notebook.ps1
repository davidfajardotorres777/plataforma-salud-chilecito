$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: notebook Windows =="

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear el entorno virtual." }
}

.\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "No se pudieron instalar las dependencias." }

Write-Host "Abriendo notebook desde la raiz del repositorio..."
.\.venv\Scripts\python.exe -m notebook --notebook-dir=. notebooks/SaludChilecito_DAO_Demo.ipynb
