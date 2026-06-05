# Guia de instalacion

## Requisitos

- Python 3.12 o superior.
- Docker Desktop o Docker Engine.
- Docker Compose.
- Git.

Links oficiales y comandos completos: [REQUISITOS.md](REQUISITOS.md).

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
http://localhost:8000/bot
```

## Instalacion manual

1. Levantar Oracle.

```bash
docker compose up -d
```

Si el contenedor habia fallado antes con `ORA-27104`, recrearlo:

```bash
docker compose down
docker compose up -d --force-recreate
```

2. Esperar hasta que el contenedor este saludable.

```bash
docker ps
docker logs -f oracle_salud_chilecito
```

3. Cargar Oracle automaticamente.

Windows:

```powershell
scripts\windows\03_cargar_oracle.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/03_cargar_oracle.sh
```

Este comando espera el contenedor, crea tablespaces, usuarios, roles, tablas,
indices, permisos y datos iniciales.

4. Preparar Python.

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Ubuntu:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

5. Probar DAO y tests.

El DAO requiere Oracle activo y cargado:

```bash
python -m src.main
```

Las pruebas del proyecto se ejecutan aparte:

```bash
python -m pytest -q
```

6. Probar interfaz grafica.

```bash
python -m src.webapp.server
```

Abrir `http://localhost:8000` desde Chrome, Edge o Firefox.

Para probar el bot conversacional, abrir `http://localhost:8000/bot`.

7. Probar notebook de demostracion.

Windows:

```powershell
scripts\windows\04_abrir_notebook.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/04_abrir_notebook.sh
```

Comando manual equivalente:

```bash
python -m notebook --notebook-dir=. notebooks/SaludChilecito_DAO_Demo.ipynb
```

## Notas

- `01_tablespaces.sql` incluye parametros de FRA y UNDO.
- El modo ARCHIVELOG requiere reiniciar la instancia en modo MOUNT, por eso se
  deja documentado dentro del script.
- Las pruebas automatizadas no necesitan una base activa; validan contrato,
  estructura y consultas DAO.
- El modo demo JSON permite usar la plataforma web aunque Oracle todavia no
  este cargado.
