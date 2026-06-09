# Documentación de API - Salud Chilecito

Versión: 1.0.0  
Base URL: `http://localhost:8000`  
Content-Type: `application/json`

## Descripción

API REST para integración con sistemas hospitalarios existentes (HIS). Permite sincronizar pacientes, médicos, turnos y agendas, además de proporcionar funcionalidades avanzadas como selección por síntomas y webhooks para sincronización bidireccional.

## Autenticación

### API Keys

La API utiliza API Keys para autenticación. Incluye la API Key en el header `Authorization`:

```
Authorization: Bearer sk_hospital_timestamp_random
```

Para obtener una API Key, utiliza el endpoint `/api/auth/api-keys`.

## Endpoints

### Autenticación

#### Crear API Key

```http
POST /api/auth/api-keys
Content-Type: application/json

{
  "hospital_name": "Hospital Eleazar Herrera Motta",
  "hospital_id": 1,
  "permissions": ["read", "write"]
}
```

**Respuesta:**
```json
{
  "api_key": "sk_hospital_eleazar_herrera_motta_20260609123456_abc123...",
  "message": "API Key creada exitosamente"
}
```

#### Validar API Key

```http
POST /api/auth/validate
Content-Type: application/json

{
  "api_key": "sk_hospital_eleazar_herrera_motta_20260609123456_abc123..."
}
```

**Respuesta:**
```json
{
  "valid": true,
  "hospital": {
    "hospital_name": "Hospital Eleazar Herrera Motta",
    "hospital_id": 1,
    "permissions": ["read", "write"]
  }
}
```

#### Listar API Keys

```http
POST /api/auth/api-keys/list
Content-Type: application/json

{
  "hospital_id": 1
}
```

#### Revocar API Key

```http
POST /api/auth/api-keys/revoke
Content-Type: application/json

{
  "api_key": "sk_hospital_eleazar_herrera_motta_20260609123456_abc123..."
}
```

#### Logs de Auditoría

```http
POST /api/auth/logs
Content-Type: application/json

{
  "hospital_id": 1,
  "event_type": "api_call"
}
```

### Webhooks

#### Registrar Webhook

```http
POST /api/webhooks/register
Content-Type: application/json

{
  "hospital_id": 1,
  "url": "https://hospital-ejemplo.com/webhooks/salud-chilecito",
  "events": ["turno.created", "turno.cancelled", "paciente.updated"],
  "secret": "opcional_secreto_para_firmar_payloads"
}
```

**Respuesta:**
```json
{
  "webhook_id": "abc123...",
  "message": "Webhook registrado exitosamente"
}
```

#### Listar Webhooks

```http
POST /api/webhooks/list
Content-Type: application/json

{
  "hospital_id": 1
}
```

#### Eliminar Webhook

```http
POST /api/webhooks/unregister
Content-Type: application/json

{
  "webhook_id": "abc123..."
}
```

#### Listar Eventos Disponibles

```http
GET /api/webhooks/events
```

**Respuesta:**
```json
{
  "events": [
    "turno.created",
    "turno.updated",
    "turno.cancelled",
    "turno.confirmed",
    "paciente.created",
    "paciente.updated",
    "medico.created",
    "medico.updated",
    "agenda.created",
    "agenda.updated",
    "agenda.deleted",
    "documento.uploaded"
  ]
}
```

#### Disparar Evento (Testing)

```http
POST /api/webhooks/trigger
Content-Type: application/json

{
  "event_type": "turno.created",
  "data": {
    "id": 1,
    "paciente_id": 1,
    "medico_id": 1,
    "fecha": "2026-06-20",
    "hora": "09:30"
  }
}
```

### Dashboard

#### Obtener Dashboard

```http
GET /api/dashboard?centro_id=1
```

**Respuesta:**
```json
{
  "centros": [...],
  "especialidades": [...],
  "medicos": [...],
  "pacientes": [...],
  "turnos": [...],
  "agendas": [...],
  "documentos": [...],
  "tarifas": [...],
  "disponibilidad": [...]
}
```

### Pacientes

#### Crear Paciente

```http
POST /api/pacientes
Content-Type: application/json

{
  "dni": "12345678",
  "nombre": "Juan Pérez",
  "telefono": "3825-123456",
  "distrito": "Chilecito",
  "obra_social": "APOS"
}
```

#### Actualizar Paciente

```http
POST /api/pacientes/1
Content-Type: application/json

{
  "dni": "12345678",
  "nombre": "Juan Pérez",
  "telefono": "3825-789012",
  "distrito": "Chilecito",
  "obra_social": "APOS"
}
```

### Turnos

#### Crear Turno

```http
POST /api/turnos
Content-Type: application/json

{
  "paciente_id": 1,
  "medico_id": 1,
  "fecha": "2026-06-20",
  "hora": "09:30",
  "motivo": "Dolor de pecho",
  "precio": 6500
}
```

#### Actualizar Turno

```http
POST /api/turnos/1
Content-Type: application/json

{
  "paciente_id": 1,
  "medico_id": 1,
  "fecha": "2026-06-20",
  "hora": "10:00",
  "motivo": "Dolor de pecho",
  "precio": 6500
}
```

#### Cambiar Estado de Turno

```http
POST /api/turnos/1/estado
Content-Type: application/json

{
  "estado": "CONFIRMADO"
}
```

#### Eliminar Turno

```http
POST /api/turnos/1/eliminar
```

### Disponibilidad

#### Obtener Disponibilidad

```http
GET /api/disponibilidad?centro_id=1&especialidad_id=3&medico_id=1
```

**Respuesta:**
```json
[
  {
    "dia_semana": "Lunes",
    "hora_inicio": "08:00",
    "hora_fin": "12:00",
    "medico": {...},
    "cupos_libres": 5,
    "cupo_diario": 10,
    "precio_estimado": 6500
  }
]
```

### Síntomas (Selección por Síntomas)

#### Listar Síntomas

```http
GET /api/sintomas
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "descripcion": "Dolor de pecho",
    "especialidad_id": 3,
    "especialidad_nombre": "Cardiología",
    "prioridad": "ALTA"
  }
]
```

#### Buscar Especialidad por Síntoma

```http
POST /api/buscar-especialidad-por-sintoma
Content-Type: application/json

{
  "sintoma": "dolor de pecho"
}
```

**Respuesta:**
```json
{
  "especialidad": {
    "id": 3,
    "nombre": "Cardiología"
  },
  "prioridad": "ALTA",
  "id_especialidad": 3
}
```

### Precios

#### Tipos de Consulta

```http
GET /api/tipos-consulta
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Consulta General",
    "descripcion": "Consulta médica de rutina"
  }
]
```

#### Precios por Especialidad

```http
GET /api/precios-especialidad?centro_id=1&especialidad_id=3
```

**Respuesta:**
```json
[
  {
    "especialidad_id": 3,
    "tipo_consulta_id": 1,
    "tipo_consulta_nombre": "Consulta General",
    "precio_min": 5000,
    "precio_max": 8000,
    "precio_estimado": 6500
  }
]
```

#### Calcular Precio

```http
POST /api/calcular_precio
Content-Type: application/json

{
  "medico_id": 1,
  "motivo": "Dolor de pecho"
}
```

**Respuesta:**
```json
{
  "base_price": 5000,
  "multiplier": 1.3,
  "estimated_price": 6500,
  "range": {
    "min": 5000,
    "max": 8000
  }
}
```

### Configuración del Hospital

#### Obtener Configuración

```http
GET /api/configuracion-hospital
```

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre_hospital": "Hospital Eleazar Herrera Motta",
    "id_centro_principal": 1,
    "color_primario": "#0f766e",
    "color_secundario": "#f59e0b",
    "logo_url": "/static/logo.svg",
    "mensaje_bienvenida": "Bienvenido al sistema de turnos",
    "politica_cancelacion": "Los turnos pueden cancelarse hasta 24 horas antes",
    "telefono": "3825-422100",
    "email": "turnos@hospitalchilecito.gov.ar"
  }
]
```

#### Crear/Actualizar Configuración

```http
POST /api/configuracion-hospital
Content-Type: application/json

{
  "nombre_hospital": "Hospital Eleazar Herrera Motta",
  "id_centro_principal": 1,
  "color_primario": "#0f766e",
  "mensaje_bienvenida": "Bienvenido al sistema de turnos"
}
```

### Documentos

#### Subir Documento

```http
POST /api/documentos
Content-Type: application/json

{
  "paciente_id": 1,
  "nombre": "Resultado de análisis",
  "tipo": "analisis",
  "contenido_base64": "SGVsbG8gV29ybGQh"
}
```

## Códigos de Estado HTTP

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Solicitud inválida
- `401 Unauthorized`: Autenticación fallida o API Key inválida
- `403 Forbidden`: No tienes permiso para acceder a este recurso
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error interno del servidor

## Errores

Todos los errores retornan un JSON con el formato:

```json
{
  "error": "Descripción del error"
}
```

## Rate Limiting

La API tiene un límite de 100 solicitudes por minuto por API Key. Si excedes este límite, recibirás un error `429 Too Many Requests`.

## Webhooks

Los webhooks permiten recibir notificaciones en tiempo real cuando ocurren eventos en Salud Chilecito.

### Payload del Webhook

```json
{
  "id": "abc123...",
  "event": "turno.created",
  "timestamp": "2026-06-09T12:34:56Z",
  "data": {
    "id": 1,
    "paciente_id": 1,
    "medico_id": 1,
    "fecha": "2026-06-20",
    "hora": "09:30",
    "estado": "CONFIRMADO"
  }
}
```

### Firma del Webhook

Si configuraste un secreto al registrar el webhook, Salud Chilecito firmará el payload con HMAC-SHA256. La firma se envía en el header `X-Webhook-Signature`:

```
X-Webhook-Signature: sha256=abc123...
```

Para verificar la firma:

```python
import hmac
import hashlib

payload = {...}
received_signature = request.headers.get("X-Webhook-Signature")
secret = "tu_secreto"

payload_str = json.dumps(payload, sort_keys=True)
expected_signature = hmac.new(
    secret.encode(),
    payload_str.encode(),
    hashlib.sha256
).hexdigest()

if hmac.compare_digest(f"sha256={expected_signature}", received_signature):
    # Firma válida
else:
    # Firma inválida
```

## Ejemplos de Integración

### Python

```python
import requests

API_BASE = "http://localhost:8000"
API_KEY = "sk_hospital_eleazar_herrera_motta_20260609123456_abc123..."

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Crear paciente
response = requests.post(
    f"{API_BASE}/api/pacientes",
    json={
        "dni": "12345678",
        "nombre": "Juan Pérez",
        "telefono": "3825-123456",
        "distrito": "Chilecito",
        "obra_social": "APOS"
    },
    headers=headers
)
print(response.json())

# Crear turno
response = requests.post(
    f"{API_BASE}/api/turnos",
    json={
        "paciente_id": 1,
        "medico_id": 1,
        "fecha": "2026-06-20",
        "hora": "09:30",
        "motivo": "Dolor de pecho"
    },
    headers=headers
)
print(response.json())
```

### JavaScript

```javascript
const API_BASE = "http://localhost:8000";
const API_KEY = "sk_hospital_eleazar_herrera_motta_20260609123456_abc123...";

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
  "Content-Type": "application/json"
};

// Crear paciente
fetch(`${API_BASE}/api/pacientes`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    dni: "12345678",
    nombre: "Juan Pérez",
    telefono: "3825-123456",
    distrito: "Chilecito",
    obra_social: "APOS"
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Crear turno
fetch(`${API_BASE}/api/turnos`, {
  method: "POST",
  headers,
  body: JSON.stringify({
    paciente_id: 1,
    medico_id: 1,
    fecha: "2026-06-20",
    hora: "09:30",
    motivo: "Dolor de pecho"
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### cURL

```bash
# Crear paciente
curl -X POST "http://localhost:8000/api/pacientes" \
  -H "Authorization: Bearer sk_hospital_eleazar_herrera_motta_20260609123456_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "dni": "12345678",
    "nombre": "Juan Pérez",
    "telefono": "3825-123456",
    "distrito": "Chilecito",
    "obra_social": "APOS"
  }'

# Crear turno
curl -X POST "http://localhost:8000/api/turnos" \
  -H "Authorization: Bearer sk_hospital_eleazar_herrera_motta_20260609123456_abc123..." \
  -H "Content-Type: application/json" \
  -d '{
    "paciente_id": 1,
    "medico_id": 1,
    "fecha": "2026-06-20",
    "hora": "09:30",
    "motivo": "Dolor de pecho"
  }'
```

## Soporte

Para preguntas o problemas de integración, contacta a:
- Email: soporte@saludchilecito.com
- Documentación: https://github.com/davidfajardotorres777/plataforma-salud-chilecito
