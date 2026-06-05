# Requisitos completos

Este archivo declara lo necesario para ejecutar Salud Chilecito en Windows y
Ubuntu sin adivinar dependencias.

## Windows

Instalar:

| Requisito | Version recomendada | Link oficial |
|---|---|---|
| Git for Windows | Ultima estable | <https://gitforwindows.org/> |
| Python | 3.12 o superior | <https://www.python.org/downloads/windows/> |
| Docker Desktop | Ultima estable | <https://www.docker.com/products/docker-desktop/> |

Instalacion con terminal usando `winget`:

```powershell
winget install --id Git.Git -e --source winget
winget install --id Python.Python.3.12 -e --source winget
winget install --id Docker.DockerDesktop -e --source winget
```

Preparar entorno Python:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Arrancar plataforma:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
scripts\windows\02_iniciar_plataforma.ps1
```

Abrir:

```text
http://localhost:8000
http://localhost:8000/bot
```

Cargar Oracle:

```powershell
scripts\windows\03_cargar_oracle.ps1
```

## Ubuntu

Instalar paquetes base:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip docker.io docker-compose-plugin
sudo usermod -aG docker $USER
```

Cerrar sesion y volver a entrar si se agrego el usuario al grupo `docker`.

Preparar entorno Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Arrancar plataforma:

```bash
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

Abrir:

```text
http://localhost:8000
http://localhost:8000/bot
```

Cargar Oracle:

```bash
bash scripts/ubuntu/03_cargar_oracle.sh
```

## Dependencias Python

El archivo `requirements.txt` declara:

```text
oracledb==2.5.1
python-dotenv==1.0.1
pytest==8.3.4
notebook==7.5.5
pandas==3.0.2
```

La interfaz web no necesita Flask, Django, Node ni npm. Usa librerias estandar
de Python, HTML, CSS y JavaScript.

El notebook de demostracion usa `notebook` y `pandas`.

## Servicios y puertos

| Servicio | Puerto | Uso |
|---|---|---|
| Web local | 8000 | Interfaz grafica, API local y bot |
| Oracle listener | 1521 | Conexion a Oracle XE |

## Variables de entorno

Copiar `.env.example` a `.env`.

```bash
cp .env.example .env
```

Valores por defecto:

```text
DB_USER=salud
DB_PASSWORD=salud123
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=XEPDB1
```

## Verificacion rapida

```bash
python scripts/check_requirements.py
python --version
git --version
docker --version
docker compose version
pip install -r requirements.txt
python -m src.webapp.server
```

En Ubuntu, si `python` no existe, usar `python3`.
