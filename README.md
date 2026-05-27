# 🏥 Salud Chilecito — Oracle + Python DAO

> **Plataforma integral de gestión de turnos y datos clínicos para el departamento de Chilecito y sus distritos.**  
> Trabajo Integrador — Bases de Datos II · Ingeniería en Sistemas · Universidad Nacional de Chilecito · 2026

[![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-blue?style=flat-square)](.)
[![Oracle](https://img.shields.io/badge/Oracle-21c_XE-red?style=flat-square&logo=oracle)](.)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python)](.)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square)](.)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](.)
[![License](https://img.shields.io/badge/Licencia-MIT-green?style=flat-square)](LICENSE)

---

## 📋 Índice

- [El problema](#-el-problema)
- [La solución](#-la-solución)
- [Tecnologías](#-tecnologías)
- [Arquitectura Oracle](#️-arquitectura-oracle)
- [Estructura del proyecto](#️-estructura-del-proyecto)
- [Instalación rápida](#-instalación-rápida)
- [Scripts SQL](#-scripts-sql)
- [Capa DAO Python](#-capa-dao-python)
- [Ejecución y tests](#-ejecución-y-tests)
- [Capturas requeridas](#-capturas-requeridas)
- [Autor](#-autor)

---

## 🔴 El problema

En el departamento de Chilecito (La Rioja), el sistema de salud presenta deficiencias estructurales que afectan especialmente a la población de menores recursos y a los habitantes de los distritos periféricos (Nonogasta, Sañogasta, Vichigasta):

| Problema | Impacto en la comunidad |
|---|---|
| **Saturación física** | Pacientes que hacen fila desde las 5 AM sin garantía de turno. |
| **Falta de información** | El ciudadano no sabe qué especialistas están disponibles sin ir personalmente. |
| **Desperdicio de recursos** | Alto ausentismo; médicos con huecos en la agenda sin poder cubrirlos. |
| **Barreras geográficas** | Habitantes de distritos alejados se trasladan solo para pedir turno. |

---

## ✅ La solución

**Salud Chilecito** digitaliza la gestión de turnos médicos. Para esta entrega (Bases de Datos II) se implementó la persistencia en **Oracle Database 21c** con una capa **DAO en Python**.

| Funcionalidad | Descripción |
|---|---|
| **Gestión de centros** | Alta, baja y modificación de centros de salud por distrito. |
| **Gestión de médicos** | Registro con matrícula, especialidad y centro asignado. |
| **Gestión de pacientes** | Padrón de pacientes con obra social y DNI único. |
| **Gestión de turnos** | Reserva con control de estado (pendiente / atendido / cancelado). |
| **Historial clínico** | Registro de diagnósticos y observaciones por paciente. |

---

## 🛠️ Tecnologías

| Tecnología | Versión | Uso |
|---|---|---|
| Oracle Database XE | 21c | Base de datos principal |
| Python | 3.12 | DAOs y scripts |
| SQLAlchemy | 2.0 | ORM / acceso a datos |
| oracledb | 2.5 | Driver Oracle Python |
| Faker | 33.1 | Generación de datos de prueba |
| pytest | 8.3 | Tests automatizados |
| Docker / Compose | latest | Contenedor Oracle multiplataforma |

---

## 🗄️ Arquitectura Oracle

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORACLE DATABASE 21c XE                     │
│                                                                  │
│  TABLESPACES                                                     │
│  ┌─────────────────────┐   ┌─────────────────────┐             │
│  │  tbs_salud_data     │   │  tbs_salud_indx     │             │
│  │  (datos, 512M→3G)   │   │  (índices, 512M→3G) │             │
│  └─────────────────────┘   └─────────────────────┘             │
│                                                                  │
│  SCHEMA: salud                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐     │
│  │ especialidad │  │ centro_salud │  │      medico       │     │
│  │──────────────│  │──────────────│  │───────────────────│     │
│  │ id (PK)      │  │ id (PK)      │  │ id (PK)           │     │
│  │ nombre       │  │ nombre       │  │ nombre            │     │
│  │ descripcion  │  │ direccion    │  │ matricula (UNIQUE)│     │
│  └──────┬───────┘  │ telefono     │  │ id_especialidad FK│     │
│         │          │ distrito     │  │ id_centro FK      │     │
│         │          │ tipo         │  └─────────┬─────────┘     │
│         │          └──────┬───────┘            │               │
│         └─────────────────┼────────────────────┘               │
│                           │                                      │
│  ┌──────────────┐  ┌──────▼────────────────────────────────┐   │
│  │   paciente   │  │                 turno                  │   │
│  │──────────────│  │───────────────────────────────────────│   │
│  │ id (PK)      │  │ id (PK)                               │   │
│  │ nombre       │  │ fecha_turno                           │   │
│  │ dni (UNIQUE) │  │ estado                                │   │
│  │ telefono     │  │ observaciones                         │   │
│  │ obra_social  │◄─┤ id_paciente FK                        │   │
│  └──────────────┘  │ id_medico FK                          │   │
│                    │ id_centro FK                          │   │
│                    └───────────────────────────────────────┘   │
│                                                                  │
│  ROLES: rl_salud_admin · rl_salud_consulta                      │
│  ARCHIVELOG + FLASH RECOVERY AREA habilitados                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estructura del proyecto

```
salud-chilecito-oracle/
│
├── docker-compose.yml          # Oracle XE 21c contenedor
├── requirements.txt            # Dependencias Python
├── .env.example                # Variables de entorno (template)
├── .gitignore
├── README.md
│
├── sql/
│   ├── 01_create_tablespaces.sql
│   ├── 02_create_users.sql
│   ├── 03_create_schema.sql
│   ├── 04_create_indexes.sql
│   ├── 05_create_roles.sql
│   ├── 06_seed_data.sql
│   └── 07_archivelog.sql
│
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py         # Engine SQLAlchemy
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── especialidad.py
│   │   ├── centro.py
│   │   ├── medico.py
│   │   ├── paciente.py
│   │   └── turno.py
│   │
│   ├── dao/
│   │   ├── __init__.py
│   │   ├── especialidad_dao.py
│   │   ├── centro_dao.py
│   │   ├── medico_dao.py
│   │   ├── paciente_dao.py
│   │   └── turno_dao.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── seed.py             # Seed con Faker
│   │
│   └── main.py                 # Demo interactivo
│
├── tests/
│   ├── __init__.py
│   └── test_dao.py             # Tests con pytest
│
└── docs/
    └── capturas/               # Capturas para el informe
```

---

## 🚀 Instalación rápida

### Requisitos previos

```bash
docker --version   # 20+
python --version   # 3.12+
git --version
```

### 1. Clonar

```bash
git clone https://github.com/davidfajardotorres777/plataforma-salud-chilecito.git
cd plataforma-salud-chilecito
```

### 2. Variables de entorno

```bash
cp .env.example .env
# No necesita modificarse para desarrollo local
```

### 3. Levantar Oracle con Docker

```bash
docker compose up -d
```

Verificar que esté corriendo:

```bash
docker ps
# oracle_salud_chilecito  STATUS: Up
```

> ⏳ La primera vez Oracle tarda ~2 minutos en inicializarse. Verificá los logs con `docker logs oracle_salud_chilecito`.

### 4. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

### 5. Ejecutar scripts SQL (en orden)

Conectate con SQL Developer o sqlplus al usuario `salud/salud123@localhost:1521/XEPDB1` y ejecutá:

```
sql/01_create_tablespaces.sql
sql/02_create_users.sql
sql/03_create_schema.sql
sql/04_create_indexes.sql
sql/05_create_roles.sql
sql/06_seed_data.sql
```

> Para habilitar Archivelog (requiere DBA): `sql/07_archivelog.sql`

### 6. Cargar datos de prueba con Faker

```bash
python -m src.services.seed
```

Resultado esperado:
```
✅ Conectado a Oracle 21c XE
🌱 Insertando especialidades...  OK (8)
🌱 Insertando centros de salud... OK (5)
🌱 Insertando médicos...          OK (20)
🌱 Insertando pacientes...        OK (50)
🌱 Insertando turnos...           OK (100)
🎉 Seed completado.
```

### 7. Ejecutar demo

```bash
python -m src.main
```

---

## 📜 Scripts SQL

| Script | Contenido |
|---|---|
| `01_create_tablespaces.sql` | `tbs_salud_data` y `tbs_salud_indx` (512M → 3G cada uno) |
| `02_create_users.sql` | Usuario `david` (DBA) y `salud` (aplicación) |
| `03_create_schema.sql` | Tablas: especialidad, centro_salud, medico, paciente, turno |
| `04_create_indexes.sql` | Índices sobre claves foráneas (tablespace `tbs_salud_indx`) |
| `05_create_roles.sql` | `rl_salud_admin` (CRUD) y `rl_salud_consulta` (SELECT) |
| `06_seed_data.sql` | Datos iniciales mínimos |
| `07_archivelog.sql` | Habilita Archivelog + Flash Recovery Area |

---

## 🐍 Capa DAO Python

Cada DAO expone operaciones CRUD completas:

```python
from src.dao.paciente_dao import PacienteDAO

# Insertar
PacienteDAO.insertar("Ana Rodríguez", "28111222", "3825-555111")

# Listar todos
pacientes = PacienteDAO.listar()

# Buscar por ID
p = PacienteDAO.buscar_por_id(1)

# Actualizar
PacienteDAO.actualizar(1, telefono="3825-999000")

# Eliminar
PacienteDAO.eliminar(1)
```

---

## 🧪 Ejecución y tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Output esperado:
# tests/test_dao.py::test_insertar_paciente     PASSED
# tests/test_dao.py::test_listar_pacientes      PASSED
# tests/test_dao.py::test_buscar_paciente       PASSED
# tests/test_dao.py::test_actualizar_paciente   PASSED
# tests/test_dao.py::test_insertar_turno        PASSED
# tests/test_dao.py::test_listar_turnos         PASSED
```

---

## 📸 Capturas requeridas

Para el informe final, guardar en `docs/capturas/`:

- [ ] Docker corriendo (`docker ps`)
- [ ] Oracle iniciado (logs del container)
- [ ] Ejecución de cada script SQL
- [ ] Tablespaces creados (`DBA_TABLESPACES`)
- [ ] Usuarios creados (`DBA_USERS`)
- [ ] Roles creados y asignados (`DBA_ROLES`)
- [ ] Archivelog habilitado (`ARCHIVE LOG LIST`)
- [ ] Flash Recovery Area configurada
- [ ] Índices creados (`USER_INDEXES`)
- [ ] Inserciones DAO (output del seed)
- [ ] Consultas DAO (output del test)
- [ ] Datos insertados (SELECT de cada tabla)

---

## ⚙️ Configuración de memoria Oracle (referencia)

Para un equipo de 8 GB RAM (50% para Oracle):

```sql
ALTER SYSTEM SET MEMORY_TARGET=4G SCOPE=SPFILE;
ALTER SYSTEM SET SGA_TARGET=2400M SCOPE=SPFILE;
ALTER SYSTEM SET PGA_AGGREGATE_TARGET=1600M SCOPE=SPFILE;
```

---

## 👤 Autor

**David Fajardo**  
Ingeniería en Sistemas — Universidad Nacional de Chilecito (UNdeC)  
Materia: Bases de Datos II — Año: 2026

---

*Bases de Datos II · Diseño Físico Oracle · UNdeC 2026*
