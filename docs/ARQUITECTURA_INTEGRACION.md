# Arquitectura de Integración con Sistemas Hospitalarios Existentes

## Problema

Los hospitales ya tienen sistemas de gestión (HIS - Hospital Information Systems). Salud Chilecito no debe reemplazar estos sistemas, sino **integrarse con ellos** para agregar valor.

## Solución: Plataforma de Integración

Salud Chilecito actúa como una **capa de integración y mejora** que se conecta a los sistemas existentes de los hospitales mediante API.

### Valor Agregado

1. **Selección por síntomas con IA** - Funcionalidad que la mayoría de los HIS no tienen
2. **Bot conversacional** - Interfaz natural para pacientes
3. **Landing pages personalizadas** - Mejor experiencia de usuario
4. **Visualización mejorada de disponibilidad** - Días y horarios específicos
5. **API moderna y estándar** - Para que otros sistemas se integren con Salud Chilecito
6. **Sincronización bidireccional** - Los cambios se reflejan en ambos sistemas

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         Paciente                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Salud Chilecito                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Landing Page │  │  Web App     │  │  Bot IA      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
│         └──────────────────┼──────────────────┘                  │
│                            ▼                                     │
│                    ┌───────────────┐                            │
│                    │   API REST   │                            │
│                    └───────┬───────┘                            │
│                            │                                     │
│         ┌──────────────────┼──────────────────┐                  │
│         ▼                  ▼                  ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Adaptador   │  │  Adaptador   │  │  Adaptador   │          │
│  │  Hospital A  │  │  Hospital B  │  │  Hospital C  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼──────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   HIS Hospital │  │   HIS Hospital │  │   HIS Hospital │
│        A        │  │        B        │  │        C        │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

## Componentes

### 1. API REST Estándar

- Endpoints RESTful con métodos HTTP apropiados (GET, POST, PUT, DELETE)
- Códigos de estado HTTP correctos
- Content-Type: application/json
- Documentación OpenAPI/Swagger
- Versionado (v1, v2)
- Rate limiting
- CORS configurado

### 2. Sistema de Autenticación y Autorización

- **API Keys**: Para integraciones entre sistemas
- **OAuth 2.0**: Para aplicaciones de terceros
- **JWT**: Para autenticación de usuarios
- Roles y permisos (admin, hospital, paciente)
- Logs de auditoría de accesos

### 3. Adaptadores (Connectors)

Cada hospital tiene un adaptador específico que:

- Traduce entre el formato de datos de Salud Chilecito y el del HIS
- Maneja la lógica de sincronización
- Implementa reintentos y manejo de errores
- Mantiene un mapeo de IDs entre sistemas

### 4. Sistema de Webhooks

- Los hospitales pueden suscribirse a eventos
- Eventos: turno_creado, turno_cancelado, paciente_actualizado
- Payload estandarizado
- Reintentos automáticos en caso de fallo
- Logs de entrega

### 5. Sistema de Sincronización

- **Sincronización en tiempo real**: Webhooks
- **Sincronización programada**: Jobs nocturnos
- **Sincronización manual**: Endpoint de trigger
- Reconciliación de datos para evitar duplicados
- Detección y resolución de conflictos

### 6. Sistema de Logs y Auditoría

- Logs de todas las operaciones de API
- Logs de sincronización
- Logs de errores
- Auditoría de accesos
- Métricas y monitoreo

## Flujo de Integración

### 1. Configuración Inicial

1. El hospital se registra en Salud Chilecito
2. Recibe API Key y credenciales
3. Configura su adaptador (mapeo de campos, endpoints)
4. Configura webhooks para recibir eventos

### 2. Sincronización de Datos Maestros

1. Pacientes: Se sincronizan usando DNI como clave única
2. Médicos: Se mapean entre sistemas
3. Especialidades: Se normalizan
4. Agendas: Se importan desde el HIS

### 3. Flujo de Reserva de Turno

```
Paciente → Salud Chilecito → API → Adaptador → HIS
         ←                ←     ←         ←
```

1. Paciente reserva turno en Salud Chilecito
2. Salud Chilecito llama al adaptador del hospital
3. Adaptador crea turno en el HIS
4. HIS confirma turno
5. Adaptador actualiza estado en Salud Chilecito
6. Paciente recibe confirmación

### 4. Sincronización Bidireccional

- Si el hospital crea un turno en su HIS, notifica a Salud Chilecito vía webhook
- Salud Chilecito actualiza su base de datos
- Si el paciente cancela en Salud Chilecito, se notifica al hospital
- Ambos sistemas permanecen sincronizados

## Funcionalidades Faltantes para Completar la Plataforma

### 1. API REST Completa y Estándar
- [ ] Documentación OpenAPI/Swagger
- [ ] Versionado de API
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Validación de datos de entrada
- [ ] Manejo de errores estandarizado
- [ ] Paginación en listados
- [ ] Filtros y ordenamiento
- [ ] Campos opcionales y expansión de relaciones

### 2. Autenticación y Autorización
- [ ] Sistema de API Keys
- [ ] OAuth 2.0
- [ ] JWT tokens
- [ ] Roles y permisos
- [ ] Logs de auditoría de accesos

### 3. Sistema de Webhooks
- [ ] Endpoint para registrar webhooks
- [ ] Sistema de envío de eventos
- [ ] Reintentos automáticos
- [ ] Logs de entrega
- [ ] Panel de administración de webhooks

### 4. Sistema de Logs y Auditoría
- [ ] Logs estructurados (JSON)
- [ ] Niveles de log (DEBUG, INFO, WARNING, ERROR)
- [ ] Rotación de logs
- [ ] Exportación de logs
- [ ] Dashboard de visualización
- [ ] Alertas en caso de errores

### 5. Adaptadores para HIS Comunes
- [ ] Adaptador genérico (REST API)
- [ ] Adaptador para sistemas HL7 FHIR
- [ ] Adaptador para bases de datos directas
- [ ] Documentación de cómo crear adaptadores personalizados

### 6. Sistema de Configuración
- [ ] Panel de configuración por hospital
- [ ] Configuración de adaptadores
- [ ] Configuración de webhooks
- [ ] Configuración de mapeos de datos
- [ ] Validación de configuración

### 7. Sistema de Monitoreo
- [ ] Métricas de uso de API
- [ ] Métricas de sincronización
- [ ] Alertas de errores
- [ ] Dashboard de salud del sistema
- [ ] Uptime monitoring

### 8. Documentación Técnica
- [ ] Guía de integración para desarrolladores
- [ ] Ejemplos de código en múltiples lenguajes
- [ ] Tutoriales paso a paso
- [ ] Referencia completa de API
- [ ] Guía de troubleshooting

### 9. Testing
- [ ] Tests unitarios
- [ ] Tests de integración
- [ ] Tests de carga
- [ ] Tests de seguridad
- [ ] Ambiente de staging

### 10. Despliegue
- [ ] Docker containers
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline
- [ ] Configuración de producción
- [ ] Backup y restore

## Ventajas Competitivas

1. **No reemplaza, mejora**: Los hospitales no necesitan cambiar sus sistemas
2. **Fácil integración**: API estándar y documentación clara
3. **Valor agregado**: Funcionalidades que los HIS no tienen (IA, selección por síntomas)
4. **Flexibilidad**: Se adapta a diferentes sistemas mediante adaptadores
5. **Escalabilidad**: Puede integrarse con múltiples hospitales
6. **Costo efectivo**: Menor costo que migrar a un nuevo sistema completo

## Próximos Pasos

1. Implementar autenticación con API Keys
2. Crear sistema de webhooks
3. Desarrollar adaptador genérico REST
4. Agregar documentación OpenAPI
5. Implementar sistema de logs
6. Crear ejemplos de integración
7. Mejorar documentación técnica
