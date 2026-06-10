# Plataforma Salud Chilecito - Presentación para el Profesor

**Autores**: Alesandro David Fajardo / Kevin Facundo Nunez  
**Universidad**: Universidad Nacional de Chilecito  
**Año**: 2026  
**Modelo de negocio**: Sistema vendido a hospitales/clínicas (single-hospital instance)

---

## 1. Introducción al Proyecto

### ¿Qué es Salud Chilecito?

Salud Chilecito es una plataforma digital completa para la gestión de centros de salud, diseñada específicamente para el contexto de Chilecito y sus distritos cercanos.

### Problema Inicial

Los hospitales y centros de salud de la región necesitaban un sistema moderno para gestionar:
- Pacientes y sus historiales clínicos
- Médicos y sus agendas
- Turnos y disponibilidad
- Documentos médicos
- Precios y tarifas

### Solución Propuesta

Una plataforma web completa con:
- Interfaz gráfica intuitiva para pacientes y personal
- Bot IA conversacional para facilitar el uso
- API REST para integración con sistemas existentes
- Sistema de gestión de turnos en tiempo real

---

## 2. Arquitectura Técnica

### Stack Tecnológico

**Backend:**
- Python 3.x
- Base de datos Oracle (producción) / JSON (desarrollo)
- Patrón DAO (Data Access Object) para abstracción de base de datos

**Frontend:**
- JavaScript vanilla
- HTML5 y CSS3
- Diseño responsivo

**Infraestructura:**
- Servidor HTTP Python (ThreadingHTTPServer)
- Sistema de archivos para almacenamiento local

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                    Plataforma Web                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Frontend   │  │   Backend    │  │   Bot IA     │ │
│  │  (JS/HTML)   │  │  (Python)    │  │  (Local)     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                 │                 │            │
│         └─────────────────┼─────────────────┘            │
│                           │                              │
│                    ┌──────▼──────┐                       │
│                    │  Capa DAO   │                       │
│                    │  (Oracle)   │                       │
│                    └─────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Características Principales

### 3.1 Gestión Completa de Centros de Salud

- **Centros**: Registro y gestión de múltiples centros de salud
- **Especialidades**: Cardiología, Pediatría, Odontología, etc.
- **Médicos**: Gestión de perfiles médicos con especialidades
- **Pacientes**: Registro completo con DNI, obra social, distrito
- **Turnos**: Sistema completo de reservas y gestión
- **Agendas**: Configuración de horarios por médico y día
- **Documentos**: Almacenamiento de documentos médicos de pacientes

### 3.2 Selección por Síntomas (Novedad)

**Problema**: Los pacientes no siempre saben qué especialidad necesitan.

**Solución**: Sistema de selección por síntomas con derivación automática.

```
Paciente: "Me duele el pecho"
    ↓
Sistema: Dolor de pecho → Cardiología
    ↓
Resultado: Se recomienda Cardiología con prioridad ALTA
```

**Beneficios**:
- Mejora la experiencia del paciente
- Reduce errores de derivación
- Facilita el uso para personas sin conocimientos médicos

### 3.3 Precios Personalizados por Tipo de Consulta

**Tipos de consulta**:
- Consulta General
- Consulta de Urgencia
- Consulta de Seguimiento
- Estudio Complementario
- Primera Consulta

**Rangos de precios por especialidad**:
- Cardiología: $5,000 - $8,000
- Pediatría: $3,000 - $5,000
- Odontología: $2,000 - $4,000

**Beneficios**:
- Transparencia en precios
- Flexibilidad para cada hospital
- Adaptación a diferentes tipos de atención

### 3.4 Configuración Personalizada por Hospital (Modelo Single-Hospital)

**Cada instancia puede personalizar**:
- Nombre del hospital
- Logo y colores (branding)
- Mensaje de bienvenida
- Políticas de cancelación
- Tiempo mínimo para cancelación

**Beneficios**:
- Identidad propia para cada hospital
- Adaptación a políticas internas
- Experiencia personalizada para pacientes

### 3.5 Disponibilidad en Tiempo Real

**Visualización mejorada**:
- Días disponibles para los próximos 7 días
- Horarios específicos por médico
- Cupos disponibles en tiempo real
- Duración de cada consulta

**Beneficios**:
- Información precisa para pacientes
- Reducción de ausencias
- Mejor gestión de agendas

### 3.6 Bot IA Conversacional

**Características**:
- Funciona localmente sin dependencias externas
- Interpreta comandos frecuentes
- Opera el mismo store de la plataforma
- No requiere API pagadas

**Comandos soportados**:
- "listar turnos"
- "crear turno para [nombre]"
- "cancelar turno [id]"
- "ver disponibilidad"

**Beneficios**:
- Accesibilidad para usuarios no técnicos
- Reducción de barreras de uso
- Costo cero (sin servicios externos)

---

## 4. Sistema de Integración con HIS (Hospital Information Systems)

### 4.1 Problema Identificado por el Profesor

**El profesor mencionó**: "Todos los hospitales ya tienen una plataforma, no quieren reemplazarla."

**Interpretación**: Los hospitales tienen sistemas de gestión (HIS) existentes y no están dispuestos a migrar a un sistema completamente nuevo.

### 4.2 Solución: Integración en lugar de Reemplazo

**Enfoque**: Salud Chilecito se integra con los sistemas existentes mediante API REST, no los reemplaza.

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Paciente   │─────→│  Salud       │─────→│   Adaptador  │
│              │      │  Chilecito   │      │   (REST/FHIR)│
└──────────────┘      └──────────────┘      └──────┬───────┘
                                                   │
                                                   ↓
                                          ┌──────────────┐
                                          │  HIS del     │
                                          │  Hospital    │
                                          │  (Existente) │
                                          └──────────────┘
```

### 4.3 Características del Sistema de Integración

**API Keys**:
- Autenticación segura para integraciones
- Generación de keys por hospital
- Permisos granulares (read, write)
- Logs de auditoría

**Webhooks**:
- Sincronización bidireccional en tiempo real
- Eventos: turno.created, turno.cancelled, paciente.updated
- Firma HMAC-SHA256 para seguridad
- Reintentos automáticos

**Adaptadores**:
- REST Adapter: Para sistemas con API REST estándar
- FHIR Adapter: Para sistemas que implementan HL7 FHIR
- Custom Adapter: Se pueden crear adaptadores personalizados

### 4.4 Ventajas Competitivas

1. **No reemplaza**: Los hospitales mantienen sus sistemas existentes
2. **Fácil integración**: API estándar y documentación clara
3. **Valor agregado**: Funcionalidades que los HIS no tienen (IA, selección por síntomas)
4. **Flexibilidad**: Se adapta a diferentes sistemas mediante adaptadores
5. **Costo efectivo**: Menor costo que migrar a un sistema completo

---

## 5. Sistema de Sincronización de Turnos Virtuales y Físicos

### 5.1 Problema Identificado

**El profesor mencionó**: "Es como un boleto de avión, cuando compras el boleto, ya lo tenés."

**Interpretación**: Cuando alguien reserva un turno, ese cupo debe estar bloqueado inmediatamente para evitar conflictos entre reservas virtuales (plataforma web) y reservas físicas (en el hospital).

### 5.2 Solución Implementada

**Validación de disponibilidad en tiempo real**:
- Verificación antes de crear cualquier turno
- Bloqueo inmediato de cupos al reservar
- Prevención de double-booking

**Campo de origen**:
- `VIRTUAL`: Reserva desde plataforma web
- `FISICO`: Reserva presencial en hospital

**Endpoints específicos**:
- `/api/turnos/verificar-disponibilidad`: Para personal del hospital
- `/api/turnos/crear-fisico`: Para reservas físicas

### 5.3 Flujo de Sincronización

**Reserva Virtual**:
1. Paciente selecciona médico, fecha y hora en plataforma web
2. Sistema verifica disponibilidad en tiempo real
3. Si hay disponibilidad, crea turno con `origen: "VIRTUAL"`
4. El cupo queda bloqueado para reservas físicas

**Reserva Física**:
1. Paciente se presenta presencialmente en hospital
2. Personal verifica disponibilidad con API
3. Si hay disponibilidad, crea turno con `origen: "FISICO"`
4. Si no hay disponibilidad (ya reservado virtualmente), se informa al paciente

### 5.4 Beneficios

- Sincronización en tiempo real entre canales
- Prevención de conflictos y double-booking
- Trazabilidad de origen de cada reserva
- Experiencia de usuario mejorada

---

## 6. Capa DAO (Data Access Object)

### 6.1 Patrones de Diseño

**Patrón DAO**: Abstracción de operaciones de base de datos en clases especializadas.

**Beneficios**:
- Separación de responsabilidades
- Reutilización de código
- Mantenibilidad mejorada
- Testabilidad

### 6.2 Métodos Principales

**Centros de Salud**:
- `listar_centros()` - Lista todos los centros
- `crear_centro()` - Crea un nuevo centro

**Médicos**:
- `listar_medicos_por_centro()` - Lista médicos por centro
- `buscar_medicos_por_especialidad()` - Busca por especialidad

**Pacientes**:
- `obtener_paciente_por_dni()` - Busca paciente por DNI
- `crear_paciente()` - Crea nuevo paciente

**Turnos**:
- `reservar_turno()` - Reserva un turno
- `cambiar_estado_turno()` - Cambia estado (PENDIENTE, CONFIRMADO, etc.)
- `disponibilidad_por_medico()` - Consulta disponibilidad

**Nuevas funcionalidades (Single-Hospital)**:
- `listar_sintomas()` - Lista síntomas con especialidades
- `buscar_especialidad_por_sintoma()` - Derivación automática
- `obtener_configuracion_hospital()` - Configuración personalizada
- `listar_tipos_consulta()` - Tipos de consulta
- `obtener_precios_por_especialidad()` - Precios por especialidad

### 6.3 Documentación

Todos los métodos incluyen:
- Docstrings detallados
- Ejemplos de uso
- Descripción de parámetros y retornos
- Explicación del propósito

---

## 7. Jupyter Notebook de Demostración

### 7.1 Propósito

El notebook sirve como recorrido guiado del proyecto para demostraciones y presentaciones.

### 7.2 Contenido

1. **Preparación**: Configuración del entorno
2. **Datos de demo**: Visualización de datos de prueba
3. **Uso del store local**: Operaciones sin Oracle
4. **Bot IA local**: Demostración del bot conversacional
5. **Capa DAO**: Ejemplos de uso del DAO
6. **Integración con HIS**: Ejemplos de API Keys, Webhooks, Adaptadores
7. **Resumen**: Síntesis para el profesor

### 7.3 Beneficios

- Demostración interactiva
- Ejemplos ejecutables
- Explicaciones paso a paso
- Visualización de datos con pandas

---

## 8. Documentación Completa

### 8.1 Documentos Disponibles

1. **README.md**: Documentación general del proyecto
2. **ARQUITECTURA_INTEGRACION.md**: Guía de integración con HIS
3. **API_OPENAPI.md**: Documentación completa de la API REST
4. **SINCRONIZACION_TURNOS.md**: Sistema de sincronización virtual/físico
5. **INTEGRACION_HOSPITAL.md**: Guía de integración específica
6. **integracion_his.py**: Ejemplos de código de integración

### 8.2 Características de la Documentación

- Ejemplos de código en Python, JavaScript y cURL
- Diagramas de arquitectura
- Guías paso a paso
- Referencias cruzadas
- Actualizada con las últimas funcionalidades

---

## 9. Comandos para Ejecutar

### 9.1 Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate      # Ubuntu
pip install -r requirements.txt
```

### 9.2 Ejecución

```bash
python scripts/check_requirements.py
python -m pytest -q
python -m src.webapp.server
```

### 9.3 Acceso

- `http://localhost:8000` - Plataforma gráfica principal
- `http://localhost:8000/bot` - Bot IA conversacional
- `http://localhost:8000/landing` - Landing page del hospital

---

## 10. Resumen para el Profesor

### 10.1 Modelo de Negocio

**Sistema vendido a hospitales/clínicas (single-hospital instance)**

Cada hospital compra su propia instancia del sistema, completamente personalizada y aislada de otras instancias.

### 10.2 Características Diferenciales

1. **Integración con HIS**: Se conecta a sistemas existentes, no los reemplaza
2. **Selección por síntomas**: Derivación automática con IA
3. **Precios personalizados**: Por especialidad y tipo de consulta
4. **Configuración por hospital**: Branding personalizado
5. **Sincronización en tiempo real**: Turnos virtuales y físicos sincronizados
6. **Bot IA local**: Sin dependencias externas ni costos
7. **API REST estándar**: Para integración con otros sistemas

### 10.3 Ventajas Competitivas

1. **No reemplaza**: Respeta sistemas existentes del hospital
2. **Fácil integración**: API estándar y documentación clara
3. **Valor agregado**: Funcionalidades que los HIS no tienen
4. **Flexible**: Se adapta a diferentes sistemas
5. **Costo efectivo**: Menor costo que migrar a sistema completo

### 10.4 Aspectos Técnicos Destacados

- **Patrón DAO**: Arquitectura limpia y mantenible
- **Validación en tiempo real**: Sincronización de turnos
- **Documentación completa**: Para desarrolladores y usuarios
- **Ejemplos prácticos**: Notebook de demostración
- **Código profesional**: Con docstrings y comentarios

---

## 11. Preguntas Frecuentes

### P: ¿Por qué no reemplazar los sistemas existentes?

R: Porque los hospitales ya tienen inversiones en sus sistemas y no están dispuestos a migrar. Salud Chilecito se integra como una capa de mejora, agregando funcionalidades que los HIS no tienen.

### P: ¿Cómo se sincronizan los turnos virtuales y físicos?

R: Mediante validación de disponibilidad en tiempo real. Cuando alguien reserva un turno (virtual o físicamente), el cupo se bloquea inmediatamente, similar a un sistema de venta de boletos de avión.

### P: ¿El Bot IA requiere servicios externos?

R: No, funciona localmente sin dependencias externas ni costos adicionales. Interpreta comandos frecuentes y opera el mismo store de la plataforma.

### P: ¿Cómo se personaliza cada instancia?

R: Cada hospital puede configurar su nombre, logo, colores, mensajes de bienvenida, políticas de cancelación, y precios según sus necesidades.

### P: ¿Qué pasa si un hospital tiene un sistema HIS diferente?

R: Salud Chilecito incluye adaptadores para diferentes tipos de sistemas (REST, FHIR) y se pueden crear adaptadores personalizados para sistemas específicos.

---

## 12. Conclusión

Salud Chilecito es una plataforma completa y profesional para la gestión de centros de salud, diseñada específicamente para el contexto de Chilecito y sus distritos cercanos.

**Puntos clave**:
- Solución integral para gestión de salud
- Integración con sistemas existentes (no reemplazo)
- Funcionalidades innovadoras (selección por síntomas, Bot IA)
- Sincronización en tiempo real de turnos
- Documentación completa y profesional
- Código bien estructurado y mantenible

**Valor para el hospital**:
- No requiere migración de sistemas existentes
- Agrega funcionalidades que los HIS no tienen
- Costo efectivo comparado con sistemas completos
- Fácil integración y uso

---

## 13. Demostración en Vivo

### Escenario 1: Reserva Virtual

1. Paciente accede a `http://localhost:8000`
2. Selecciona sus síntomas: "Dolor de pecho"
3. Sistema recomienda: Cardiología
4. Paciente elige médico, fecha y hora
5. Sistema verifica disponibilidad en tiempo real
6. Turno reservado con `origen: "VIRTUAL"`

### Escenario 2: Reserva Física

1. Paciente se presenta en el hospital
2. Personal verifica disponibilidad con API
3. Si hay disponibilidad, reserva turno con `origen: "FISICO"`
4. Si no hay disponibilidad (ya reservado virtualmente), informa al paciente

### Escenario 3: Bot IA

1. Paciente accede a `http://localhost:8000/bot`
2. Escribe: "listar turnos"
3. Bot responde con lista de turnos disponibles
4. Paciente escribe: "crear turno para Juan Pérez"
5. Bot crea el turno automáticamente

---

## 14. Recursos Adicionales

- **GitHub**: https://github.com/davidfajardotorres777/plataforma-salud-chilecito
- **Documentación**: docs/
- **Ejemplos**: examples/
- **Notebook**: notebooks/SaludChilecito_DAO_Demo.ipynb

---

**Fin de la presentación**

¿Preguntas?
