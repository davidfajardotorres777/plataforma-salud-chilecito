# Pitch Comercial - Salud Chilecito para Hospitales

## Resumen Ejecutivo (Elevator Pitch)

Salud Chilecito es una solución de gestión de turnos y pacientes que se instala por hospital/centro. Ofrecemos entrega llave en mano: el hospital compra su propia instancia con branding personalizado y acceso vía subdominio propio (ej: turnos.hospitalchilecito.com).

**No reemplazamos el sistema existente del hospital, nos integramos con él.**

---

## Beneficios Clave para el Hospital

### 1. **No Reemplaza, Mejora**
- El hospital mantiene su sistema de gestión (HIS) actual
- Salud Chilecito se integra como capa de presentación para pacientes
- Sin riesgo de migración ni pérdida de datos

### 2. **Selección por Síntomas con Derivación Inteligente**
- Los pacientes describen sus síntomas (ej: "me duele mucho el pecho")
- El sistema sugiere automáticamente la especialidad correcta (Cardiología)
- Considera la edad del paciente (menores de 10 años → Pediatría)
- Reduce errores de derivación y turnos equivocados

### 3. **Experiencia de Usuario Superior**
- Landing page personalizada con branding del hospital
- Visualización clara de disponibilidad (próximos 7 días)
- Reserva de turnos desde cualquier dispositivo
- Notificaciones automáticas

### 4. **Integración con HIS Existente**
- API REST estándar para sincronización
- Webhooks para actualizaciones en tiempo real
- Adaptadores para diferentes sistemas (REST, FHIR)
- Sincronización bidireccional de turnos y pacientes

### 5. **Control Total de Tarifas y Configuración**
- Precios personalizados por especialidad y tipo de consulta
- Configuración de políticas de cancelación
- Mensajes de bienvenida personalizados
- Colores y logo del hospital

### 6. **Costo Efectivo**
- Menor inversión que migrar a un sistema completo
- Implementación rápida (2-4 semanas)
- Sin necesidad de reentrenar al personal administrativo

---

## Modelo de Negocio y Precios

### Opción A: Licencia Perpetua + Mantenimiento Anual
- **Licencia única**: $15,000 USD (instalación en servidor del hospital)
- **Mantenimiento anual**: $3,000 USD (actualizaciones, soporte, parches de seguridad)
- **Incluye**: Instalación, configuración, capacitación inicial, integración básica con HIS

### Opción B: Suscripción Mensual (SaaS)
- **Plan Hospital**: $500 USD/mes
- **Incluye**: Hosting, mantenimiento, soporte, actualizaciones automáticas
- **Contrato mínimo**: 12 meses

### Servicios Adicionales (Opcionales)
- **Integración avanzada con HIS**: $2,000 - $5,000 USD (según complejidad)
- **Capacitación adicional**: $500 USD por sesión (4 horas)
- **Soporte prioritario 24/7**: $200 USD/mes adicional
- **Desarrollo de funcionalidades custom**: $100 USD/hora

---

## Qué Entregamos (Entrega Llave en Mano)

### 1. Instalación y Configuración
- Instalación del software en servidor del hospital o cloud privado
- Configuración de base de datos (Oracle o PostgreSQL)
- Configuración de dominio y SSL
- Configuración de backup y monitoreo

### 2. Integración con HIS
- Desarrollo de adaptador personalizado para el sistema del hospital
- Configuración de webhooks para sincronización
- Mapeo de datos entre sistemas
- Pruebas de integración end-to-end

### 3. Onboarding y Capacitación
- Carga inicial de médicos, especialidades y agendas
- Configuración de tarifas y políticas
- Capacitación para secretarias (2 sesiones de 4 horas)
- Capacitación para administradores (1 sesión de 4 horas)
- Manual de usuario y documentación técnica

### 4. Soporte y Mantenimiento
- Soporte por email durante horario laboral (9-18hs)
- Actualizaciones de software incluidas
- Parches de seguridad críticos
- Acceso a portal de soporte con documentación y FAQs

---

## Tiempos de Implementación

### Fase 1: Preparación (1 semana)
- Reunión inicial con equipo del hospital
- Análisis del sistema HIS existente
- Definición de requisitos de integración
- Firma de contrato y condiciones

### Fase 2: Instalación (1 semana)
- Instalación de software en servidor
- Configuración de base de datos
- Configuración de dominio y SSL
- Pruebas de funcionamiento básico

### Fase 3: Integración (1-2 semanas)
- Desarrollo de adaptador HIS
- Configuración de webhooks
- Pruebas de sincronización
- Resolución de incidencias

### Fase 4: Onboarding (1 semana)
- Carga de datos iniciales
- Capacitación del personal
- Pruebas piloto con usuarios reales
- Ajustes finales

**Total: 4-5 semanas desde el inicio hasta la puesta en producción**

---

## SLA (Service Level Agreement)

### Disponibilidad
- **99.5% uptime mensual** para sistemas en cloud propio
- **99% uptime mensual** para sistemas en servidor del hospital
- Tiempo máximo de recuperación: 4 horas

### Tiempos de Respuesta
- **Crítico**: 4 horas (sistema caído, datos corruptos)
- **Alto**: 8 horas (funcionalidad principal no disponible)
- **Medio**: 24 horas (funcionalidad secundaria afectada)
- **Bajo**: 48 horas (consultas generales, mejoras)

### Soporte
- Email: soporte@saludchilecito.com
- Teléfono: disponible para clientes con plan de soporte prioritario
- Portal de soporte: docs.saludchilecito.com/soporte

---

## Garantías

### Garantía de Funcionamiento
- 30 días de garantía desde la puesta en producción
- Si no se cumplen los funcionalidades principales, devolución del 100%
- Corrección de bugs críticos sin costo adicional

### Garantía de Seguridad
- Cumplimiento con estándares de seguridad OWASP
- Encriptación de datos en tránsito (TLS 1.3)
- Encriptación de datos en reposo (AES-256)
- Auditorías de seguridad anuales

### Garantía de Datos
- Backup diario automatizado
- Retención de backups por 90 días
- Recuperación de datos garantizada en caso de pérdida

---

## Comparativa con Competidores

| Característica | Salud Chilecito | Sistema HIS Tradicional | Otros SaaS de Turnos |
|---------------|-----------------|------------------------|---------------------|
| **No reemplaza HIS** | ✅ Sí | ❌ No | ❌ No |
| **Selección por síntomas** | ✅ Sí | ❌ No | ❌ No |
| **Derivación por edad** | ✅ Sí | ❌ No | ❌ No |
| **Integración con HIS** | ✅ Sí | N/A | ⚠️ Limitada |
| **Branding personalizado** | ✅ Sí | ⚠️ Limitado | ⚠️ Limitado |
| **Precio** | 💰 Bajo | 💰💰💰 Muy Alto | 💰💰 Medio |
| **Tiempo de implementación** | 4-5 semanas | 6-12 meses | 2-4 semanas |
| **Costo de migración** | $0 | 💰💰💰 Muy Alto | 💰 Medio |

---

## ROI para el Hospital

### Ahorro Estimado Anual
- **Reducción de llamadas telefónicas**: 30-40% (pacientes reservan online)
- **Reducción de turnos ausentes**: 15-20% (recordatorios automáticos)
- **Reducción de errores de derivación**: 25% (sistema inteligente)
- **Ahorro en personal administrativo**: 1-2 FTE equivalentes

### Ingresos Adicionales
- **Aumento de ocupación**: 10-15% (mejor visibilidad de disponibilidad)
- **Mejor aprovechamiento de agendas**: 5-10% (optimización de horarios)

### Cálculo de ROI (Ejemplo Hospital Mediano)
- **Inversión inicial**: $15,000 USD
- **Mantenimiento anual**: $3,000 USD
- **Ahorro anual estimado**: $25,000 USD
- **ROI primer año**: 56%
- **Payback**: 8 meses

---

## Casos de Uso

### Caso 1: Hospital Público
- **Problema**: Pacientes no saben qué especialidad necesitan
- **Solución**: Selección por síntomas con derivación inteligente
- **Resultado**: Reducción del 40% en consultas innecesarias

### Caso 2: Clínica Privada
- **Problema**: Alta tasa de ausencias en turnos
- **Solución**: Recordatorios automáticos y reserva online fácil
- **Resultado**: Reducción del 25% en ausencias

### Caso 3: Centro de Salud
- **Problema**: Sistema HIS antiguo sin interfaz para pacientes
- **Solución**: Integración sin reemplazo
- **Resultado**: Mejora en satisfacción del paciente sin cambiar sistema interno

---

## Pasos Técnicos Rápidos (MVP)

### 1. Crear el centro en Salud Chilecito
```bash
POST /api/centros
{
  "nombre": "Hospital Chilecito",
  "slug": "hospital-chilecito",
  "direccion": "Av. Principal 123",
  "distrito": "Chilecito",
  "telefono": "3825-100000",
  "tipo": "PUBLICO"
}
```

### 2. Cargar médicos y especialidades
```bash
POST /api/medicos
POST /api/especialidades
```

### 3. Importar agendas
```bash
POST /api/agendas/import
[
  {"medico_id": 1, "dia_semana": "Lunes", "hora_inicio": "08:00", "hora_fin": "12:00", "duracion_minutos": 30, "cupo_diario": 8}
]
```

### 4. Probar reservas
```bash
POST /api/turnos
{
  "paciente_id": 1,
  "medico_id": 1,
  "fecha": "2026-06-20",
  "hora": "09:30",
  "motivo": "Dolor de pecho"
}
```

---

## Demostración de Uso

### Obtener disponibilidades
```bash
GET /api/disponibilidad?centro_id=1
```

### Buscar especialidad por síntoma
```bash
POST /api/buscar-especialidad-por-sintoma
{"sintoma": "dolor de pecho"}
```

### Calcular precio estimado
```bash
POST /api/calcular_precio
{"especialidad_id": 3, "motivo": "dolor de pecho"}
```

### Obtener horarios disponibles
```bash
GET /api/horarios-disponibles?medico_id=1&fecha=2026-06-20
```

---

## Materiales de Venta Disponibles

- [ ] Presentación ejecutiva (PPT)
- [ ] Demo en vivo de la plataforma
- [ ] Casos de éxito y testimonios
- [ ] Análisis de ROI personalizado
- [ ] Propuesta formal con términos y condiciones
- [ ] Contrato de servicio y SLA
- [ ] Guía de implementación técnica

---

## Próximos Pasos

1. **Reunión de descubrimiento**: Entender necesidades específicas del hospital
2. **Demo personalizada**: Mostrar la plataforma con datos del hospital
3. **Propuesta formal**: Documento con precios, tiempos y alcances
4. **Prueba piloto**: Período de prueba de 30 días (opcional)
5. **Firma de contrato**: Inicio del proyecto
6. **Implementación**: 4-5 semanas hasta puesta en producción

---

## Contacto

**Ventas**: ventas@saludchilecito.com  
**Teléfono**: +54 3825 XXX XXX  
**Web**: www.saludchilecito.com  
**Documentación**: docs.saludchilecito.com
