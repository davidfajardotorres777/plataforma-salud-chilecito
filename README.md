# Salud Chilecito

Plataforma digital para gestionar centros de salud, pacientes, medicos, turnos,
historial clinico y documentos asociados a la atencion medica en Chilecito y
sus distritos cercanos.

El proyecto combina una base Oracle, una capa DAO en Python, scripts de carga,
un notebook de demostracion, una interfaz web operativa y un bot local para
usar la plataforma por conversacion.

**Modelo de negocio**: Sistema vendido a hospitales/clínicas (single-hospital instance)  
**Autor**: Alesandro David Fajardo / Kevin Facundo Nunez  
**Universidad**: Universidad Nacional de Chilecito  
**Ano**: 2026

## Que se puede hacer

- Registrar y consultar centros de salud.
- Registrar y corregir datos de pacientes.
- Consultar medicos y especialidades.
- Consultar disponibilidad por medico, dia, horario y cupos.
- Crear, editar, confirmar, cancelar o eliminar turnos.
- Calcular un precio estimado segun especialidad y tipo de centro.
- Adjuntar documentos de pacientes.
- Ver documentos guardados con metadatos y vista previa.
- Usar una interfaz grafica desde el navegador.
- Usar una plataforma conversacional con Bot IA local.
- Ejecutar consultas y operaciones desde la capa DAO.
- Cargar y validar la base Oracle con comandos automatizados.
- **Integrarse con sistemas hospitalarios existentes (HIS) mediante API REST**
- **Sincronizar datos bidireccionalmente con webhooks**
- **Usar autenticación con API Keys para integraciones seguras**

## Nuevas funcionalidades (Modelo Single-Hospital)

### Selección por síntomas
Los pacientes pueden seleccionar sus síntomas y el sistema sugiere automáticamente la especialidad adecuada:
- Dolor de pecho → Cardiología
- Dolor de muelas → Odontología
- Fiebre en niños → Pediatría

### Precios por tipo de consulta
Cada especialidad tiene rangos de precios según el tipo de consulta:
- Consulta General
- Consulta de Urgencia
- Consulta de Seguimiento
- Estudio Complementario
- Primera Consulta

### Disponibilidad en tiempo real
Visualización de horarios disponibles por médico y fecha específica.

### Configuración personalizada por hospital
Cada instancia puede personalizar:
- Nombre del hospital
- Logo y colores
- Mensaje de bienvenida
- Políticas de cancelación

## Sistema de Integración con HIS (Hospital Information Systems)

**Problema**: Los hospitales ya tienen sistemas de gestión (HIS) y no quieren reemplazarlos.

**Solución**: Salud Chilecito se integra con los sistemas existentes mediante API REST, no los reemplaza.

### ¿Cómo funciona la integración?

Esta plataforma es **COMPLEMENTARIA** al sistema existente del hospital, no lo reemplaza. Funciona como una capa de inteligencia que mejora la gestión de turnos sin interrumpir las operaciones actuales.

#### Arquitectura de Integración

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA ACTUAL DEL HOSPITAL               │
│  (Sistema HIS existente - Hospital Information System)       │
│  - Gestión de pacientes                                      │
│  - Historia clínica                                          │
│  - Facturación                                               │
│  - Administración                                            │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ API REST / Webhooks
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              PLATAFORMA SALUD CHILECITO (Nuestra)            │
│  - Gestión de turnos inteligente                             │
│  - Selección por síntomas                                    │
│  - Multi-hospital (centros múltiples)                        │
│  - Asignación automática de especialistas                    │
│  - Disponibilidad en tiempo real                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ Sincronización bidireccional
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    BASE DE DATOS ORACLE                      │
│  - Datos persistentes                                        │
│  - Historial de turnos                                       │
│  - Configuración de hospitales                               │
└─────────────────────────────────────────────────────────────┘
```

### Métodos de Integración Disponibles

#### 1. **Integración vía API REST (Recomendada)**
- El hospital proporciona acceso a su API existente
- Nuestra plataforma se conecta para:
  - Sincronizar datos de pacientes
  - Exportar turnos al sistema del hospital
  - Obtener disponibilidad de médicos
- **Beneficio**: Sincronización en tiempo real

#### 2. **Integración vía Webhooks**
- El hospital envía notificaciones a nuestra plataforma
- Eventos: nuevo paciente, cancelación de turno, cambio de disponibilidad
- **Beneficio**: Actualizaciones automáticas sin consultas constantes

#### 3. **Integración vía Exportación/Importación**
- Exportación periódica de datos (CSV, JSON, XML)
- Importación de turnos desde nuestra plataforma
- **Beneficio**: No requiere acceso directo al sistema

#### 4. **Integración Manual (Fase Piloto)**
- Ingreso manual de datos para probar el sistema
- Migración gradual de datos
- **Beneficio**: Bajo riesgo, permite validar el sistema

### Características del Sistema de Integración

- **API Keys**: Autenticación segura para integraciones entre sistemas
- **Webhooks**: Sincronización bidireccional en tiempo real
- **Adaptadores**: Soporte para diferentes tipos de HIS (REST, FHIR)
- **Logs de auditoría**: Registro de todas las operaciones de integración
- **Documentación OpenAPI**: API estándar y bien documentada para desarrolladores

### Endpoints de Integración

- `POST /api/auth/api-keys` - Generar API Keys para autenticación
- `POST /api/auth/validate` - Validar API Keys
- `POST /api/webhooks/register` - Registrar webhooks para sincronización
- `POST /api/webhooks/trigger` - Disparar eventos de prueba

### Tipos de Adaptadores

- **REST Adapter**: Para sistemas HIS con API REST estándar
- **FHIR Adapter**: Para sistemas que implementan el estándar HL7 FHIR
- **Custom Adapter**: Se pueden crear adaptadores personalizados

### Flujo de Implementación

1. **Evaluación y Diagnóstico (1-2 semanas)**
   - Análisis del sistema HIS del hospital
   - Identificación de puntos de integración
   - Evaluación de capacidades de API

2. **Configuración Técnica (2-3 semanas)**
   - Configuración de la plataforma
   - Integración técnica (API keys, webhooks)
   - Pruebas de conexión

3. **Migración de Datos (1-2 semanas)**
   - Importación de datos históricos
   - Validación de datos
   - Aprobación del hospital

4. **Capacitación (1 semana)**
   - Capacitación del personal
   - Documentación
   - Soporte técnico

5. **Piloto (2-4 semanas)**
   - Implementación en un centro
   - Monitoreo de errores
   - Ajustes basados en feedback

6. **Despliegue Completo (1-2 semanas)**
   - Expansión a todos los centros
   - Soporte intensivo
   - Monitoreo continuo

### Beneficios de la Integración

1. **No reemplaza**: Los hospitales mantienen sus sistemas existentes
2. **Fácil integración**: API estándar y documentación clara
3. **Valor agregado**: Funcionalidades que los HIS no tienen (IA, selección por síntomas)
4. **Flexibilidad**: Se adapta a diferentes sistemas mediante adaptadores
5. **Costo efectivo**: Menor costo que migrar a un nuevo sistema completo
6. **Seguridad**: Encriptación SSL/TLS, autenticación con API keys
7. **Escalabilidad**: Soporte para múltiples centros de salud

### Documentación

- [Arquitectura de Integración](docs/ARQUITECTURA_INTEGRACION.md) - Guía completa de integración
- [Documentación de API](docs/API_OPENAPI.md) - Referencia completa de la API REST
- [Ejemplos de Integración](examples/integracion_his.py) - Ejemplos de código
- [Presentación para Hospitales](PRESENTACION_VENTA_HOSPITALES.md) - Guía de venta e implementación

### Preguntas Frecuentes

**¿Necesitan cambiar su sistema actual?**
No. Nuestra plataforma se integra con el sistema existente del hospital.

**¿Es seguro?**
Sí. Utilizamos encriptación de datos (SSL/TLS), autenticación vía API keys, y cumplimos con normas de seguridad de datos.

**¿Cuánto tiempo toma la implementación?**
6-12 semanas dependiendo del tamaño del hospital y la complejidad de la integración.

**¿Pueden probar antes de comprar?**
Sí. Ofrecemos demo de 30 días y piloto gratuito en un centro.

## Componentes principales

| Componente | Ruta | Descripcion |
|---|---|---|
| Base Oracle | `sql/` | Scripts ordenados para tablespaces, usuarios, roles, tablas, indices, seed y validaciones |
| DAO Python | `src/dao/` | Clases que encapsulan las operaciones contra Oracle |
| Modelos | `src/models/` | Dataclasses del dominio de salud |
| Configuracion | `src/config/` y `.env.example` | Conexion y variables de entorno |
| Plataforma web | `src/webapp/` | Interfaz grafica, API local, store JSON y Bot IA |
| Notebook | `notebooks/SaludChilecito_DAO_Demo.ipynb` | Recorrido guiado del proyecto |
| Datos demo | `data/demo_seed.json` | Datos iniciales para usar la plataforma sin preparar Oracle |
| Scripts | `scripts/` | Instalacion, inicio, pruebas y carga automatica |
| Pruebas | `tests/` | Validaciones del SQL, DAO, scripts, web, bot y notebook |
| Documentacion | `docs/` | Guias de instalacion, arquitectura, uso y checklist |

## Enfoque del producto

Salud Chilecito esta pensado como un sistema que una institucion de salud puede instalar para administrar su propia atencion. El paciente entra al portal de ese hospital o clinica, ve los medicos disponibles, consulta dias y horarios, elige un turno y deja registrado el motivo de consulta.

La institucion mantiene el control desde el panel operativo:

- Define centros, medicos, especialidades y agenda.
- Ve cupos disponibles por medico.
- Registra pacientes y corrige datos cargados con error.
- Crea, edita, confirma, cancela o elimina turnos.
- Adjunta documentos clinicos y revisa su contenido.
- Usa precios estimados por especialidad y tipo de centro.
- Puede operar desde la interfaz grafica o desde el Bot IA local.

## Estructura del proyecto

```text
plataforma-salud-chilecito/
|-- docker-compose.yml
|-- sql/
|-- src/
|   |-- config/
|   |-- dao/
|   |-- models/
|   |-- services/
|   `-- webapp/
|-- data/demo_seed.json
|-- notebooks/SaludChilecito_DAO_Demo.ipynb
|-- scripts/
|-- tests/
`-- README.md
```

## Requisitos

Instalar:

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

## Instalacion rapida

### 1. Clonar el repositorio

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

### 3. Crear archivo de entorno

Windows:

```powershell
Copy-Item .env.example .env
```

Ubuntu:

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

### 4. Levantar Oracle

```bash
docker compose up -d
```

Si el contenedor ya se habia iniciado antes y el log muestra `ORA-27104`,
recrearlo para aplicar la memoria compartida declarada en `docker-compose.yml`:

```bash
docker compose down
docker compose up -d --force-recreate
```

### 5. Cargar la base

Windows:

```powershell
.\scripts\windows\03_cargar_oracle.ps1
```

En PowerShell el `.\` inicial es necesario para ejecutar scripts ubicados en la
carpeta actual del proyecto.

Ubuntu:

```bash
bash scripts/ubuntu/03_cargar_oracle.sh
```

Ese comando espera el contenedor, crea la estructura fisica, usuarios, roles,
tablas, indices, permisos y datos iniciales.

### 6. Probar DAO y tests

El DAO usa Oracle, por eso este comando requiere que el contenedor este iniciado
y que la carga anterior haya terminado bien:

```bash
python -m src.main
```

Para ejecutar las pruebas:

```bash
python -m pytest -q
```

Si el entorno virtual ya esta activado, tambien se puede usar:

```bash
pytest -q
```

### 7. Abrir la plataforma

Windows:

```powershell
.\scripts\windows\02_iniciar_plataforma.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/02_iniciar_plataforma.sh
```

Abrir en el navegador:

```text
http://localhost:8000
```

Abrir el bot:

```text
http://localhost:8000/bot
```

## Uso rapido sin preparar Oracle

La plataforma web tambien funciona en modo demo JSON. Ese modo usa:

```text
data/demo_seed.json
runtime/salud_chilecito_data.json
runtime/uploads/
```

Esto permite probar altas, ediciones, turnos, documentos y bot desde el
navegador aunque la base Oracle todavia no este cargada.

## Instalación para un hospital específico

Para implementar este sistema en un hospital:

1. **Configurar la instancia del hospital**
   ```python
   from dao import SaludDAO
   dao = SaludDAO()
   dao.crear_configuracion_hospital(
       nombre_hospital="Hospital Mi Hospital",
       id_centro_principal=1,
       color_primario="#0066cc",
       mensaje_bienvenida="Bienvenido al sistema de turnos"
   )
   ```

2. **Cargar síntomas específicos del hospital**
   ```python
   dao.crear_sintoma("Dolor de pecho", id_especialidad=3, prioridad="ALTA")
   ```

3. **Configurar precios por especialidad**
   ```python
   # Ver docs/INTEGRACION_HOSPITAL.md para más detalles
   ```

Para más información sobre integración con sistemas existentes del hospital, ver `docs/INTEGRACION_HOSPITAL.md`.

## Notebook de demostracion

Abrir con el script del sistema operativo.

Windows:

```powershell
.\scripts\windows\04_abrir_notebook.ps1
```

Ubuntu:

```bash
bash scripts/ubuntu/04_abrir_notebook.sh
```

Tambien se puede abrir manualmente desde la raiz del repositorio:

```bash
python -m notebook --notebook-dir=. notebooks/SaludChilecito_DAO_Demo.ipynb
```

El notebook muestra:

- Lectura del seed local.
- Visualizacion de datos con pandas.
- Creacion de paciente y turno en modo demo.
- Uso del Bot IA local.
- Estructura de la capa DAO.
- Comandos para conectar la app con Oracle.

## DAO Python

La capa DAO concentra las consultas y operaciones contra Oracle. Esto evita que
el SQL quede disperso y permite que cada parte del dominio tenga su clase.

Ejemplo:

```python
from src.config import OracleDatabase
from src.dao import CentroDAO, MedicoDAO, TurnoDAO

db = OracleDatabase()

centros = CentroDAO(db).listar()
medicos_cardio = MedicoDAO(db).buscar_por_especialidad("Cardiologia")
proximos = TurnoDAO(db).listar_proximos(limite=5)
agenda_cardio = TurnoDAO(db).disponibilidad_por_medico(id_medico=1)

print(centros)
print(medicos_cardio)
print(proximos)
print(agenda_cardio)
```

DAOs incluidos:

| DAO | Responsabilidad |
|---|---|
| `CentroDAO` | Centros de salud y busqueda por distrito |
| `EspecialidadDAO` | Catalogo de especialidades |
| `MedicoDAO` | Medicos, centros y especialidades |
| `PacienteDAO` | Pacientes, busqueda por DNI y actualizacion de contacto |
| `AgendaDAO` | Agenda disponible de medicos |
| `TurnoDAO` | Reserva, listado y cambio de estado de turnos |
| `HistorialDAO` | Historial clinico del paciente |

**Nuevos métodos (Modelo Single-Hospital)**

| Categoría | Método | Descripción |
|---|---|---|
| **Síntomas (NUEVO)** | `listar_sintomas()` | Lista todos los síntomas con sus especialidades |
| | `buscar_especialidad_por_sintoma(sintoma)` | Busca especialidad recomendada por síntoma |
| | `crear_sintoma(...)` | Crea un nuevo síntoma |
| **Configuración Hospital (NUEVO)** | `obtener_configuracion_hospital(id)` | Obtiene configuración del hospital |
| | `crear_configuracion_hospital(...)` | Configura una instancia de hospital |
| **Precios (NUEVO)** | `listar_tipos_consulta()` | Lista tipos de consulta |
| | `obtener_precios_por_especialidad(centro, especialidad)` | Precios por especialidad |
| | `obtener_precio_estimado_por_tipo(...)` | Precio estimado por tipo de consulta |
| **Disponibilidad Mejorada (NUEVO)** | `obtener_turnos_disponibles_por_medico(medico, dias)` | Turnos disponibles por médico |
| | `obtener_medicos_disponibles_por_especialidad(...)` | Médicos disponibles por especialidad |
| | `obtener_horarios_disponibles(medico, fecha)` | Horarios específicos disponibles |

## Plataforma web

La interfaz grafica esta disponible en:

```text
http://localhost:8000
```

Funciones:

- Dashboard con indicadores.
- Gestion de centros.
- Gestion de pacientes.
- Agenda de turnos.
- Disponibilidad por medico con dia, horario, cupos y precio estimado.
- Edicion y eliminacion de turnos.
- Carga y vista previa de documentos.
- Busqueda general por paciente, medico, centro, DNI, distrito o estado.

## Bot IA local

El bot esta disponible en:

```text
http://localhost:8000/bot
```

Ejemplos:

```text
listar pacientes
listar centros
listar medicos
mostrar horarios disponibles y precios
listar turnos
listar sintomas
que especialidad para dolor de pecho
que doctor para fiebre
crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS
editar paciente 1 telefono 3825-999000
crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo dolor de pecho
editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado
eliminar turno 2
crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal
ver documento 1
```

El bot funciona localmente y opera sobre los mismos datos que la interfaz web.

## Scripts SQL

| Orden | Script | Contenido |
|---|---|---|
| 1 | `sql/01_tablespaces.sql` | Tablespaces y configuracion fisica |
| 2 | `sql/02_users_roles.sql` | Usuarios y roles |
| 3 | `sql/03_schema.sql` | Tablas, claves primarias, foraneas y checks |
| 4 | `sql/04_indexes.sql` | Indices |
| 5 | `sql/05_seed.sql` | Datos iniciales |
| 6 | `sql/06_validate.sql` | Consultas de validacion |
| 7 | `sql/07_security_checks.sql` | Validaciones de permisos y seguridad |
| 8 | `sql/08_new_features.sql` | Nuevas tablas para modelo single-hospital (síntomas, configuración, precios) |
| 9 | `sql/09_seed_new_features.sql` | Datos iniciales para nuevas funcionalidades |

## Scripts disponibles

| Sistema | Script | Uso |
|---|---|---|
| Windows | `scripts/windows/01_instalar.ps1` | Instala herramientas base y dependencias Python |
| Windows | `scripts/windows/02_iniciar_plataforma.ps1` | Levanta Oracle, prepara la base e inicia la web |
| Windows | `scripts/windows/03_cargar_oracle.ps1` | Carga la base Oracle automaticamente |
| Windows | `scripts/windows/04_abrir_notebook.ps1` | Abre el notebook de demostracion |
| Ubuntu | `scripts/ubuntu/01_instalar.sh` | Instala herramientas base y dependencias Python |
| Ubuntu | `scripts/ubuntu/02_iniciar_plataforma.sh` | Levanta Oracle, prepara la base e inicia la web |
| Ubuntu | `scripts/ubuntu/03_cargar_oracle.sh` | Carga la base Oracle automaticamente |
| Ubuntu | `scripts/ubuntu/04_abrir_notebook.sh` | Abre el notebook de demostracion |
| Ambos | `python scripts/check_requirements.py` | Verifica requisitos locales |
| Ambos | `python -m pytest -q` | Ejecuta pruebas |

## Pruebas

Ejecutar:

```bash
python -m pytest -q
```

Con el entorno virtual activado tambien funciona:

```bash
pytest -q
```

Las pruebas cubren:

- Contrato de scripts SQL.
- Estructura de DAOs.
- Scripts de instalacion y carga.
- Plataforma web.
- Bot IA.
- Notebook y dependencias.

## Documentacion adicional

| Documento | Contenido |
|---|---|
| [docs/REQUISITOS.md](docs/REQUISITOS.md) | Requisitos completos |
| [docs/INSTALACION.md](docs/INSTALACION.md) | Instalacion paso a paso |
| [docs/USO_PLATAFORMA.md](docs/USO_PLATAFORMA.md) | Uso operativo |
| [docs/BOT_IA.md](docs/BOT_IA.md) | Comandos del bot |
| [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md) | Arquitectura del sistema |
| [docs/CHECKLIST.md](docs/CHECKLIST.md) | Checklist del proyecto |
| [docs/INTEGRACION_HOSPITAL.md](docs/INTEGRACION_HOSPITAL.md) | Integración con sistemas internos del hospital (Modelo Single-Hospital) |

## Autores

Alesandro David Fajardo  
Kevin Facundo Nunez  
Ingenieria en Sistemas - Universidad Nacional de Chilecito  
2026
