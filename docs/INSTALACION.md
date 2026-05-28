# Guia de instalacion

## Requisitos

- Python 3.12 o superior.
- Docker Desktop o Docker Engine.
- Git.
- SQL Developer, SQLcl o SQL*Plus para ejecutar scripts Oracle.

Links oficiales y comandos completos: [REQUISITOS.md](REQUISITOS.md).

Windows:

- Git for Windows: <https://gitforwindows.org/>
- Python: <https://www.python.org/downloads/windows/>
- Docker Desktop: <https://www.docker.com/products/docker-desktop/>
- SQL Developer: <https://www.oracle.com/database/sqldeveloper/>

Ubuntu:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip default-jdk docker.io docker-compose-plugin
```

`default-jdk` es necesario para SQL Developer en Ubuntu.

## Instalacion automatica

Windows PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
scripts\windows\01_instalar.ps1
scripts\windows\02_iniciar_plataforma.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/01_instalar.sh
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

La plataforma queda disponible en:

```text
http://localhost:8000
```

## Pasos

1. Levantar Oracle.

```bash
docker compose up -d
```

2. Esperar hasta que el contenedor este saludable.

```bash
docker ps
docker logs -f oracle_salud_chilecito
```

3. Conectar como administrador.

Datos por defecto del contenedor:

```text
host: localhost
puerto: 1521
servicio: XEPDB1
usuario admin: system
password admin: oracle
```

4. Ejecutar:

```sql
@sql/01_tablespaces.sql
@sql/02_users_roles.sql
```

5. Conectar como `salud/salud123@localhost:1521/XEPDB1` y ejecutar:

```sql
@sql/03_schema.sql
@sql/04_indexes.sql
@sql/05_seed.sql
@sql/06_validate.sql
@sql/07_security_checks.sql
```

6. Preparar Python.

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Ubuntu:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

7. Probar DAO.

```bash
python -m src.main
pytest -q
```

8. Probar interfaz grafica.

```bash
python -m src.webapp.server
```

Abrir `http://localhost:8000` desde Chrome, Edge o Firefox.

## Notas de entrega

- `01_tablespaces.sql` incluye parametros de FRA y UNDO.
- El modo ARCHIVELOG requiere reiniciar la instancia en modo MOUNT, por eso se
  deja documentado dentro del script.
- Las pruebas automatizadas no necesitan una base activa; validan contrato,
  estructura y consultas DAO. La ejecucion real contra Oracle se hace con
  `python -m src.main`.
