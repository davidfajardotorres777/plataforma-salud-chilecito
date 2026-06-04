# Salud Chilecito - Oracle, DAO, Notebook y plataforma web

Trabajo integrador de Base de Datos II para una plataforma de gestion de turnos,
pacientes, centros de salud y documentos clinicos del departamento Chilecito.

El proyecto esta preparado para que el docente pueda revisarlo de cuatro formas:

1. **Base Oracle**: scripts SQL con tablespaces, usuarios, roles, tablas,
   indices, seed y validaciones.
2. **Capa DAO en Python**: clases `CentroDAO`, `PacienteDAO`, `TurnoDAO`,
   `MedicoDAO`, `AgendaDAO`, etc.
3. **Notebook de demostracion**:
   `notebooks/SaludChilecito_DAO_Demo.ipynb`.
4. **Plataformas de uso real**:
   `http://localhost:8000` para interfaz grafica y
   `http://localhost:8000/bot` para Bot IA local.

> SQL Developer no es obligatorio. La carga de Oracle se hace con Docker y
> scripts Python. SQL Developer queda solo como opcion para inspeccionar tablas.

## Indice

- [Que resuelve](#que-resuelve)
- [Que incluye la entrega](#que-incluye-la-entrega)
- [Comparacion con las referencias](#comparacion-con-las-referencias)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Instalacion rapida](#instalacion-rapida)
- [Notebook de demostracion](#notebook-de-demostracion)
- [Uso del DAO](#uso-del-dao)
- [Plataforma grafica y Bot IA](#plataforma-grafica-y-bot-ia)
- [Scripts SQL](#scripts-sql)
- [Pruebas](#pruebas)
- [Documentacion](#documentacion)

## Que resuelve

En Chilecito muchas personas todavia deben trasladarse o hacer fila para saber
si hay turnos disponibles. Salud Chilecito centraliza:

- Centros de salud de Chilecito, Nonogasta, Sanogasta y otros distritos.
- Medicos y especialidades.
- Pacientes y datos de contacto.
- Turnos con estado, precio y motivo.
- Documentos del paciente, como ordenes, estudios, recetas, imagenes o PDF.

La idea es que el sistema pueda usarse como una plataforma digital real y no
solo como un conjunto de scripts sueltos.

## Que incluye la entrega

| Parte | Archivo/carpeta | Para que sirve |
|---|---|---|
| SQL Oracle | `sql/` y `dbscripts.sql` | Crea tablespaces, usuarios, roles, tablas, indices, datos y validaciones |
| Docker | `docker-compose.yml` | Levanta Oracle XE localmente |
| Configuracion | `.env.example` | Declara usuario, password, host, puerto y servicio Oracle |
| DAO Python | `src/dao/` | Encapsula consultas y operaciones contra Oracle |
| Modelos | `src/models/` | Dataclasses del dominio de salud |
| Demo web | `src/webapp/` | Interfaz grafica, API local, Bot IA y store JSON |
| Notebook | `notebooks/SaludChilecito_DAO_Demo.ipynb` | Recorrido guiado para explicar el proyecto |
| Scripts | `scripts/windows/` y `scripts/ubuntu/` | Instalacion, inicio y carga automatica en Windows y Ubuntu |
| Tests | `tests/` | Pruebas de SQL, DAO, scripts, web y bot |
| Docs | `docs/` | Guias completas de instalacion, requisitos, arquitectura y uso |

## Comparacion con las referencias

Este repositorio toma lo mejor de las referencias revisadas:

- Del proyecto del profesor `hdrobins/dao`: la idea principal es la capa DAO,
  los scripts de base y el uso de notebooks como forma de demostracion.
- De `valentin-31/SAVIA`: se toma el estilo de entrega clara, con README
  completo, seed, DAO, notebook y pasos reproducibles.
- De `kevlarod/UniShare`: se toma la presencia de notebook de demo y archivos
  de configuracion visibles para ejecutar el proyecto.

La diferencia es que Salud Chilecito esta adaptado a Oracle, Base de Datos II y
al dominio sanitario de turnos, pacientes, centros y documentos.

## Estructura del repositorio

```text
plataforma-salud-chilecito/
|-- README.md
|-- requirements.txt
|-- docker-compose.yml
|-- .env.example
|-- dbscripts.sql
|-- notebooks/
|   `-- SaludChilecito_DAO_Demo.ipynb
|-- sql/
|   |-- 01_tablespaces.sql
|   |-- 02_users_roles.sql
|   |-- 03_schema.sql
|   |-- 04_indexes.sql
|   |-- 05_seed.sql
|   |-- 06_validate.sql
|   `-- 07_security_checks.sql
|-- src/
|   |-- config/
|   |-- dao/
|   |-- models/
|   |-- services/
|   `-- webapp/
|-- data/
|   `-- demo_seed.json
|-- scripts/
|   |-- windows/
|   `-- ubuntu/
|-- docs/
`-- tests/
```

## Requisitos

Requisitos obligatorios:

- Git.
- Python 3.12 o superior.
- Docker Desktop en Windows o Docker Engine en Ubuntu.
- Docker Compose.

Dependencias Python declaradas en `requirements.txt`:

```text
oracledb==2.5.1
python-dotenv==1.0.1
pytest==8.3.4
notebook==7.5.5
pandas==3.0.2
```

Herramientas opcionales:

- SQL Developer: solo para mirar tablas o ejecutar SQL manualmente.
- SQL*Plus: no hace falta para el flujo normal del proyecto.

Guia detallada: [docs/REQUISITOS.md](docs/REQUISITOS.md).

## Instalacion rapida

### 1. Clonar

```bash
git clone https://github.com/davidfajardotorres777/plataforma-salud-chilecito.git
cd plataforma-salud-chilecito
```

### 2. Crear entorno Python

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

### 3. Preparar variables

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Ubuntu:

```bash
cp .env.example .env
```

### 4. Levantar Oracle

```bash
docker compose up -d
```

### 5. Cargar Oracle automaticamente

Windows:

```powershell
scripts\windows\03_cargar_oracle.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/03_cargar_oracle.sh
```

Ese paso crea tablespaces, usuarios, roles, tablas, indices y datos iniciales.
No requiere abrir SQL Developer.

### 6. Probar DAO y tests

```bash
python -m src.main
pytest -q
```

### 7. Abrir plataforma web

Windows:

```powershell
scripts\windows\02_iniciar_plataforma.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

Abrir:

```text
http://localhost:8000
http://localhost:8000/bot
```

## Notebook de demostracion

El notebook principal esta en:

```text
notebooks/SaludChilecito_DAO_Demo.ipynb
```

Ejecutarlo:

```bash
jupyter notebook notebooks/SaludChilecito_DAO_Demo.ipynb
```

El notebook muestra:

- Carga del seed local.
- Vista de datos con pandas.
- Creacion de paciente y turno usando el store de demo.
- Uso del Bot IA local.
- Estructura de la capa DAO.
- Como conectar con Oracle real usando los scripts.

## Uso del DAO

El DAO es la parte central para la materia. La aplicacion no trabaja con SQL
disperso en cualquier archivo; las consultas se agrupan por responsabilidad.

Ejemplo:

```python
from src.config import OracleDatabase
from src.dao import CentroDAO, MedicoDAO, TurnoDAO

db = OracleDatabase()

centros = CentroDAO(db).listar()
medicos_cardio = MedicoDAO(db).buscar_por_especialidad("Cardiologia")
proximos = TurnoDAO(db).listar_proximos(limite=5)

print(centros)
print(medicos_cardio)
print(proximos)
```

DAOs incluidos:

| DAO | Responsabilidad |
|---|---|
| `CentroDAO` | Centros de salud por distrito y alta de centros |
| `EspecialidadDAO` | Catalogo de especialidades |
| `MedicoDAO` | Medicos, centros y especialidades |
| `PacienteDAO` | Pacientes, busqueda por DNI y actualizacion de contacto |
| `AgendaDAO` | Agenda disponible de medicos |
| `TurnoDAO` | Reserva, listado y cambio de estado de turnos |
| `HistorialDAO` | Historial clinico del paciente |

## Plataforma grafica y Bot IA

La entrega incluye dos plataformas de uso:

### Panel grafico

```text
http://localhost:8000
```

Permite:

- Crear y editar centros.
- Crear y editar pacientes.
- Crear, editar, cambiar estado y eliminar turnos.
- Adjuntar documentos.
- Ver documentos con metadatos y vista previa.

### Bot IA local

```text
http://localhost:8000/bot
```

Ejemplos de comandos:

```text
listar pacientes
crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS
editar paciente 1 telefono 3825-999000
crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control
editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado
eliminar turno 2
crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal
ver documento 1
```

El bot no usa servicios externos ni claves de API. Es local y opera los mismos
datos de la plataforma web.

## Scripts SQL

| Orden | Script | Contenido |
|---|---|---|
| 1 | `sql/01_tablespaces.sql` | Tablespaces, FRA y configuracion fisica |
| 2 | `sql/02_users_roles.sql` | Usuario propietario, usuarios de consulta y roles |
| 3 | `sql/03_schema.sql` | Tablas, claves primarias, foraneas y checks |
| 4 | `sql/04_indexes.sql` | Indices en tablespace separado |
| 5 | `sql/05_seed.sql` | Datos iniciales de Chilecito |
| 6 | `sql/06_validate.sql` | Consultas de validacion |
| 7 | `sql/07_security_checks.sql` | Validaciones de roles y seguridad |

`dbscripts.sql` funciona como archivo de referencia general, pero el flujo
ordenado esta en la carpeta `sql/`.

## Pruebas

Ejecutar:

```bash
pytest -q
```

Las pruebas verifican:

- Contrato de scripts SQL.
- Estructura y uso de DAOs.
- Scripts de instalacion y carga.
- Plataforma web.
- Bot IA.
- Notebook y dependencias de Jupyter.

## Documentacion

| Documento | Contenido |
|---|---|
| [docs/REQUISITOS.md](docs/REQUISITOS.md) | Instalacion completa Windows/Ubuntu |
| [docs/INSTALACION.md](docs/INSTALACION.md) | Guia paso a paso |
| [docs/USO_PLATAFORMA.md](docs/USO_PLATAFORMA.md) | Uso operativo de la web y el bot |
| [docs/BOT_IA.md](docs/BOT_IA.md) | Comandos del bot conversacional |
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Componentes y decisiones tecnicas |
| [docs/CHECKLIST.md](docs/CHECKLIST.md) | Checklist de entrega |

## Autores

Alesandro David Fajardo  
Kevin Facundo Nunez  
Ingenieria en Sistemas - Universidad Nacional de Chilecito  
Base de Datos II - 2026
