Integración con sistemas internos del hospital (Modelo Single-Hospital)

Resumen rápido

- Objetivo: explicar cómo integrar un sistema de gestión de turnos (externo o interno) con Salud Chilecito.
- Alcance: intercambio de agendas y turnos, sincronización de pacientes y documentos, recomendaciones de seguridad.
- **Nuevo modelo**: Cada hospital tiene su propia instancia del sistema. Los pacientes acceden directamente al sistema del hospital (ej: hospital-chilecito.com).

Endpoints relevantes (modo demo / API local)

**Dashboard y disponibilidad**

- GET `/api/dashboard` — dashboard (acepta `?centro_id=<id>` para filtrar por centro).
- GET `/api/disponibilidad` — lista agendas y cupos. Filtros opcionales: `?centro_id=<id>&especialidad_id=<id>&medico_id=<id>`.

**Turnos**

- POST `/api/turnos` — crear turno. Payload: `paciente_id`, `medico_id`, `fecha`, `hora`, `motivo`, opcional `precio`.
- POST `/api/turnos/<id>` — actualizar un turno (mismo payload que crear).
- POST `/api/turnos/<id>/estado` — cambiar estado: `{ "estado": "CONFIRMADO" }`.

**Pacientes y centros**

- POST `/api/pacientes` — crear paciente.
- POST `/api/pacientes/<id>` — actualizar paciente.
- POST `/api/centros` — crear centro (administrativo).

**Agendas (nuevo)**

- POST `/api/agendas` — crear agenda para un medico. Payload: `medico_id`, `dia_semana`, `hora_inicio`, `hora_fin`, `duracion_minutos`, `cupo_diario`.
- POST `/api/agendas/import` — importar múltiples agendas (batch). Payload: lista de agendas (mismo formato).

**Cálculo de precio (nuevo)**

- POST `/api/calcular_precio` — estimar precio basado en especialidad/medico y motivo/síntomas. Payload: `medico_id` O `especialidad_id`, `motivo` (opcional `centro_id`). Retorna: `base_price`, `multiplier`, `estimated_price`, `range`.

**Selección por síntomas (nuevo)**

- GET `/api/sintomas` — lista todos los síntomas disponibles con sus especialidades asociadas.
- POST `/api/buscar-especialidad-por-sintoma` — busca la especialidad recomendada según el síntoma. Payload: `sintoma` (texto). Retorna: `especialidad`, `prioridad`, `id_especialidad`.
- GET `/api/precios-especialidad` — obtiene rangos de precios por especialidad y tipo de consulta. Filtros: `centro_id`, `especialidad_id`.

**Disponibilidad mejorada (nuevo)**

- GET `/api/turnos-disponibles` — lista turnos disponibles por médico en los próximos N días. Filtros: `medico_id`, `dias` (default 7).
- GET `/api/horarios-disponibles` — lista horarios específicos disponibles para un médico en una fecha. Filtros: `medico_id`, `fecha` (YYYY-MM-DD).

**Documentos**

- POST `/api/documentos` — subir documento (base64 en `contenido_base64`).

Recomendación de integración (patrón)

1. Identificar el centro (hospital) en la integración
   - Si integras con un sistema del hospital, usa `centro_id` (si existe) o configura el `slug` del centro en Salud Chilecito y pasa ese slug.
   - Salud Chilecito soporta detectar centro por slug o por subdominio (ej: `hospital-mi-centro.example.com` → slug `hospital-mi-centro`).

2. Sincronización de agendas (realtime o batch)
   - Preferible: Webhooks desde el HIS (Hospital Information System) hacia un endpoint que tú implementes. Cuando cambie la agenda envía: `medico_id`, `fecha`, `hora_inicio`, `hora_fin`, `duracion_minutos`, `cupo_diario`.
   - Alternativa: job nocturno que exporta CSV/JSON y lo importa desde Salud Chilecito usando un pequeño adaptor (script que llama a `/api/centros`, `/api/turnos`).

3. Sincronización de pacientes
   - Evitar duplicados: usar identificador nacional (DNI) como clave primaria para emparejar pacientes.
   - Si no hay match, crear paciente con `POST /api/pacientes`.

4. Conflictos y reconcilación
   - Si un turno fue reservado en ambos sistemas, usar una regla de prioridad (ej. HIS tiene prioridad) y reconciliar mediante un job que compare `fecha/hora/medico/paciente`.

Seguridad y autenticación

- Producción: desplegar Salud Chilecito detrás de un proxy seguro (TLS) y añadir un proxy que exija autenticación (API keys o JWT).
- Recomiendo exponer un adaptador que valide una API key enviada por el HIS y que realice las llamadas al API interno.

Checklist de integración

- [ ] Definir mapping de `medico_id`, `centro_id`, `especialidad_id` entre HIS y Salud Chilecito.
- [ ] Definir si la integración será push (webhooks) o pull (sync job).
- [ ] Configurar un entorno de pruebas con datos demo (`data/demo_seed.json`).
- [ ] Probar creación de pacientes y turnos con llamadas a la API local.
- [ ] Implementar autenticación para el adaptador.
- [ ] Monitorizar logs y crear alertas en caso de desincronización.
- [ ] Configurar síntomas y mapeo a especialidades para el hospital específico.
- [ ] Configurar rangos de precios por especialidad y tipo de consulta.
- [ ] Configurar la apariencia del sistema (logo, colores, mensaje de bienvenida).

Ejemplo rápido (crear turno via curl)

curl -X POST "http://localhost:8000/api/turnos" -H "Content-Type: application/json" -d '{"paciente_id":1,"medico_id":1,"fecha":"2026-06-20","hora":"09:30","motivo":"Dolor de pecho"}'

Ejemplo nuevo (flujo por síntomas)

1. Buscar especialidad por síntoma:
   curl -X POST "http://localhost:8000/api/buscar-especialidad-por-sintoma" -H "Content-Type: application/json" -d '{"sintoma":"dolor de pecho"}'

2. Obtener precios por especialidad:
   curl "http://localhost:8000/api/precios-especialidad?centro_id=1&especialidad_id=3"

3. Obtener horarios disponibles:
   curl "http://localhost:8000/api/horarios-disponibles?medico_id=1&fecha=2026-06-20"
