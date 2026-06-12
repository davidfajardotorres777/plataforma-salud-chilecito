# Funcionalidades Hospitalarias - Plataforma Salud Chilecito
============================================================

## Visión General

La plataforma Salud Chilecito es un sistema completo de gestión hospitalaria que proporciona todas las funcionalidades necesarias para la operación eficiente de un centro de salud.

## Funcionalidades Principales

### 1. Gestión de Pacientes
- Registro completo de pacientes
- Historial clínico digital
- Gestión de datos demográficos
- Seguimiento de tratamientos
- Integración con turnos

### 2. Gestión de Turnos
- Sistema de reserva de turnos online
- Disponibilidad en tiempo real
- Confirmación de turnos
- Cancelación y reprogramación
- Recordatorios automáticos

### 3. Gestión de Recetas Médicas
- Generación de recetas digitales
- Control de medicamentos
- Dosificación y frecuencia
- Historial de recetas por paciente
- Validación de interacciones

### 4. Gestión de Estudios Médicos
- Solicitud de estudios (laboratorio, radiología, etc.)
- Seguimiento de estados
- Resultados digitales
- Archivo de estudios
- Integración con turnos

### 5. Gestión de Internaciones
- Registro de ingresos
- Control de camas y habitaciones
- Seguimiento de evolución
- Gestión de altas médicas
- Reportes de estadía

### 6. Sistema de Notificaciones
- Notificaciones push
- Email de verificación
- Recordatorios de turnos
- Alertas de resultados
- Mensajes del sistema

### 7. Sistema de Seguridad
- Autenticación con JWT
- Roles de usuario (paciente, médico, admin)
- Validación de contraseñas
- Rate limiting
- Protección CSRF
- Sanitización de inputs

### 8. Sistema de Auditoría
- Logging de todas las acciones
- Auditoría de seguridad
- Logs de errores
- Logs de rendimiento
- Rastreabilidad completa

### 9. Sistema de Backups
- Backups automáticos de MongoDB
- Backups de Redis
- Retención configurable
- Restauración de backups
- Compresión de backups

### 10. Sistema de Reportes
- Reportes de turnos
- Reportes de pacientes
- Reportes de médicos
- Reportes financieros
- Exportación a CSV y JSON

### 11. Dashboard Profesional
- Vista general del sistema
- Estadísticas en tiempo real
- Lista de turnos recientes
- Panel de notificaciones
- Métricas clave

## Arquitectura Técnica

### Base de Datos
- **MongoDB**: Base de datos principal
- **Redis**: Caché y gestión de sesiones

### Tecnologías
- **Backend**: Python 3.13
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: JWT + bcrypt
- **Email**: SMTP
- **Testing**: pytest

### Módulos Principales

#### dao_mongodb.py
Capa de acceso a datos para MongoDB con métodos para:
- Gestión de pacientes, médicos, centros
- Gestión de turnos y agendas
- Gestión de recetas médicas
- Gestión de estudios médicos
- Gestión de notificaciones
- Gestión de internaciones

#### auth.py
Servicio de autenticación con:
- Registro de pacientes
- Verificación de email
- Login con JWT
- Gestión de tokens

#### redis_cache.py
Cliente de caché Redis con:
- Caché de datos
- Gestión de sesiones
- TTL automático

#### security.py
Módulo de seguridad con:
- Validación de contraseñas
- Sanitización de inputs
- Rate limiting
- Protección CSRF

#### audit_logger.py
Sistema de auditoría con:
- Logging de acciones
- Logging de errores
- Logging de seguridad
- Logging de rendimiento

#### backup_manager.py
Gestor de backups con:
- Backups de MongoDB
- Backups de Redis
- Restauración
- Retención

#### report_generator.py
Generador de reportes con:
- Reportes de turnos
- Reportes de pacientes
- Reportes de médicos
- Reportes financieros
- Exportación

## Modelos de Datos

### Paciente
```python
@dataclass
class Paciente:
    dni: str
    nombre: str
    email: Optional[str]
    telefono: Optional[str]
    fecha_nacimiento: Optional[date]
    obra_social: Optional[str]
    distrito: Optional[str]
    centro_id: Optional[str]
    fecha_alta: datetime
    activo: bool
```

### Receta
```python
@dataclass
class Receta:
    paciente_id: str
    medico_id: str
    turno_id: Optional[str]
    medicamentos: List[MedicamentoRecetado]
    diagnostico: Optional[str]
    indicaciones: Optional[str]
    fecha_emision: datetime
    activa: bool
```

### Estudio Médico
```python
@dataclass
class EstudioMedico:
    paciente_id: str
    medico_id: str
    tipo_estudio: TipoEstudio
    descripcion: str
    indicaciones: Optional[str]
    fecha_solicitud: datetime
    fecha_realizacion: Optional[datetime]
    fecha_resultado: Optional[datetime]
    resultado: Optional[str]
    estado: EstadoEstudio
    archivo_url: Optional[str]
```

### Internación
```python
@dataclass
class Internacion:
    paciente_id: str
    medico_id: str
    centro_id: str
    tipo: TipoInternacion
    motivo_ingreso: str
    diagnostico_ingreso: Optional[str]
    fecha_ingreso: datetime
    fecha_alta: Optional[datetime]
    estado: EstadoInternacion
    habitacion: Optional[str]
    cama: Optional[str]
```

## API Endpoints

### Autenticación
- `POST /api/auth/registro` - Registro de paciente
- `POST /api/auth/login` - Login de usuario
- `GET /api/auth/verificar-email?token={token}` - Verificar email

### Turnos
- `GET /api/turnos` - Listar turnos
- `POST /api/turnos` - Crear turno
- `PUT /api/turnos/{id}` - Actualizar turno
- `DELETE /api/turnos/{id}` - Cancelar turno

### Recetas
- `GET /api/recetas/paciente/{id}` - Obtener recetas del paciente
- `POST /api/recetas` - Crear receta

### Estudios
- `GET /api/estudios/paciente/{id}` - Obtener estudios del paciente
- `POST /api/estudios` - Crear estudio
- `PUT /api/estudios/{id}/estado` - Actualizar estado

### Internaciones
- `GET /api/internaciones/paciente/{id}` - Obtener internaciones del paciente
- `GET /api/internaciones/activas` - Obtener internaciones activas
- `POST /api/internaciones` - Crear internación
- `PUT /api/internaciones/{id}/alta` - Dar alta

### Reportes
- `GET /api/reportes/turnos` - Reporte de turnos
- `GET /api/reportes/pacientes` - Reporte de pacientes
- `GET /api/reportes/medicos` - Reporte de médicos
- `GET /api/reportes/financiero` - Reporte financiero

## Seguridad

### Autenticación
- Tokens JWT con expiración de 24 horas
- Hashing de contraseñas con bcrypt
- Verificación de email obligatoria

### Autorización
- Roles: PACIENTE, MEDICO, ADMIN
- Control de acceso por rol
- Validación de permisos

### Protección
- Rate limiting por IP
- Sanitización de inputs
- Protección CSRF
- Validación de datos

## Despliegue

### Desarrollo Local
```bash
# Iniciar MongoDB y Redis
docker compose up -d

# Instalar dependencias
pip install -r requirements.txt

# Cargar datos iniciales
python seed_mongodb.py

# Iniciar servidor
python -m src.webapp.server
```

### Producción (Render)
El archivo `render.yaml` configura automáticamente:
- Servicio web Python
- MongoDB gratuito
- Redis gratuito
- Variables de entorno
- SSL/HTTPS automático

## Testing

### Ejecutar Tests
```bash
# Tests de integración
python test_integracion.py

# Tests de funcionalidades hospitalarias
pytest tests/test_hospitalarios.py

# Todos los tests
pytest
```

## Soporte y Mantenimiento

### Logs
- Logs de aplicación: `logs/audit.log`
- Logs de errores: `logs/error.log`
- Logs de seguridad: `logs/security.log`

### Backups
- Directorio de backups: `backups/`
- Backups automáticos: Configurables
- Retención: 30 días por defecto

### Monitoreo
- Métricas de rendimiento
- Logs de auditoría
- Alertas de seguridad
- Estadísticas de uso

## Documentación Adicional

- [README.md](../README.md) - Documentación general
- [README_RENDER.md](../README_RENDER.md) - Guía de despliegue en Render
- [DESPLIEGUE_PRODUCCION.md](DESPLIEGUE_PRODUCCION.md) - Guía de despliegue en producción
- [ARQUITECTURA_INTEGRACION.md](ARQUITECTURA_INTEGRACION.md) - Arquitectura de integración
- [API_OPENAPI.md](API_OPENAPI.md) - Documentación de API

## Contacto

- **Autor**: Alesandro David Fajardo / Kevin Facundo Nunez
- **Universidad**: Universidad Nacional de Chilecito
- **Año**: 2026
- **Email**: soporte@saludchilecito.com
