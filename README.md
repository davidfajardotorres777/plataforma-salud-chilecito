# Salud Chilecito

Plataforma digital para gestionar centros de salud, pacientes, medicos, turnos, historial clinico y documentos asociados a la atencion medica en Chilecito y sus distritos cercanos.

**Autor:** Alesandro David Fajardo / Kevin Facundo Nunez  
**Universidad:** Universidad Nacional de Chilecito  
**Ano:** 2026

---

## Estructura del proyecto

```
plataforma-salud-chilecito/
├── dao.py                    # Capa de acceso a datos (accesible desde git y Jupyter)
├── config_vars.py            # Variables de conexion a Oracle
├── setup_db.py               # Inicializacion de la base de datos
├── seed.py                   # Carga de datos de prueba
├── newDemo.ipynb             # Notebook de demostracion
├── db_models/                # Modelos de datos (dataclasses)
│   ├── __init__.py
│   ├── paciente.py
│   ├── centro.py
│   ├── medico.py
│   ├── turno.py
│   ├── agenda.py
│   ├── especialidad.py
│   └── historial.py
├── sql/                      # Scripts SQL ordenados
│   ├── 01_tablespaces.sql
│   ├── 02_users_roles.sql
│   ├── 03_schema.sql
│   ├── 04_indexes.sql
│   ├── 05_seed.sql
│   ├── 06_validate.sql
│   └── 07_security_checks.sql
├── scripts/                  # Scripts de instalacion y carga
├── tests/                    # Pruebas del proyecto
├── docs/                     # Documentacion adicional
├── docker-compose.yml        # Contenedor Oracle
├── libs.txt                  # Dependencias Python
├── .env.example              # Variables de entorno de ejemplo
└── .gitignore
```

---

## Instalacion rapida

### 1. Clonar el repositorio

```bash
git clone https://github.com/davidfajardotorres777/plataforma-salud-chilecito.git
cd plataforma-salud-chilecito
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r libs.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
```

Valores por defecto:
```
DB_USER=salud
DB_PASSWORD=salud123
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=XEPDB1
```

### 4. Levantar Oracle

```bash
docker compose up -d
```

### 5. Inicializar la base de datos

```bash
python setup_db.py
```

### 6. Cargar datos de prueba

```bash
python seed.py
```

### 7. Probar el DAO

```bash
python -c "from dao import SaludDAO; dao = SaludDAO(); print(dao.ping()); dao.cerrar()"
```

### 8. Abrir el notebook de demostracion

```bash
jupyter notebook newDemo.ipynb
```

---

## Uso del DAO

`dao.py` es la unica interfaz entre el sistema y Oracle. Todos los metodos reciben parametros del dominio de salud.

```python
from dao import SaludDAO

dao = SaludDAO()

# Centros
centros = dao.listar_centros()
centros_chilecito = dao.listar_centros(distrito="Chilecito")

# Medicos
medicos_cardio = dao.buscar_medicos_por_especialidad("Cardiologia")
medicos_hospital = dao.listar_medicos_por_centro(1)

# Pacientes
pacientes = dao.listar_pacientes()
paciente = dao.obtener_paciente_por_dni("40111222")

# Turnos
turnos = dao.listar_turnos_proximos(limite=5)
dao.reservar_turno(id_paciente=1, id_medico=1, id_centro=1, fecha_turno="2026-06-20 09:30")
dao.cambiar_estado_turno(id_turno=1, estado_nuevo="CONFIRMADO")

# Disponibilidad
disponibilidad = dao.disponibilidad_por_medico(id_medico=1)

# Historial
historial = dao.listar_historial_por_paciente(id_paciente=1)

dao.cerrar()
```

---

## Metodos disponibles en el DAO

| Categoria | Metodo | Descripcion |
|-----------|--------|-------------|
| **Centros** | `listar_centros(distrito?)` | Lista centros, opcionalmente filtrados por distrito |
| | `crear_centro(...)` | Crea un nuevo centro de salud |
| **Especialidades** | `listar_especialidades()` | Lista todas las especialidades |
| | `obtener_especialidad_por_nombre(nombre)` | Busca especialidad por nombre |
| **Medicos** | `listar_medicos_por_centro(id_centro)` | Medicos de un centro |
| | `buscar_medicos_por_especialidad(especialidad)` | Medicos por especialidad |
| | `crear_medico(...)` | Crea un nuevo medico |
| **Pacientes** | `listar_pacientes()` | Lista todos los pacientes |
| | `obtener_paciente_por_dni(dni)` | Busca paciente por DNI |
| | `crear_paciente(...)` | Crea un nuevo paciente |
| | `actualizar_contacto_paciente(...)` | Actualiza telefono/email |
| **Turnos** | `listar_turnos_proximos(limite?)` | Proximos turnos programados |
| | `reservar_turno(...)` | Reserva un nuevo turno |
| | `cambiar_estado_turno(id, estado)` | Cambia estado del turno |
| | `eliminar_turno(id)` | Elimina un turno |
| | `disponibilidad_por_medico(id)` | Cupos disponibles por medico |
| **Historial** | `listar_historial_por_paciente(id)` | Historial clinico del paciente |
| | `registrar_historial(...)` | Registra un nuevo registro clinico |

---

## Notebook de demostracion

El notebook `newDemo.ipynb` muestra:

1. Conexion a la base de datos
2. Conteo de registros por tabla
3. Listado de especialidades, centros, medicos y pacientes
4. Busqueda por DNI y especialidad
5. Agenda de medicos
6. Turnos proximos y disponibilidad
7. Historial clinico
8. Precio estimado por especialidad y centro
9. Operaciones CRUD de ejemplo
10. Estructura de tablas, columnas, constraints e indices de Oracle

---

## Autores

- Alesandro David Fajardo
- Kevin Facundo Nunez

Ingenieria en Sistemas - Universidad Nacional de Chilecito  
2026
