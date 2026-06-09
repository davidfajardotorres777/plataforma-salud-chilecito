# Sistema de Sincronización de Turnos Virtuales y Físicos

## Problema

El sistema original no sincronizaba los turnos virtuales (reservados por la plataforma web) con los turnos físicos (reservados presencialmente en el hospital). Esto causaba conflictos cuando un paciente reservaba un turno virtualmente y otro paciente lo reservaba físicamente en el mismo horario.

El profesor describió el problema como: "Es como un boleto de avión, cuando compras el boleto, ya lo tenés". Esto significa que cuando alguien reserva un turno, ese cupo debe estar bloqueado inmediatamente para evitar double-booking.

## Solución Implementada

### 1. Validación de Disponibilidad en Tiempo Real

Se implementó validación de disponibilidad antes de crear cualquier turno, independientemente del origen (virtual o físico).

**Método**: `_verificar_disponibilidad_turno(data, medico_id, fecha, hora)`

Este método verifica si existe un turno en el mismo horario para el mismo médico, independientemente del origen del turno (VIRTUAL o FISICO).

```python
def _verificar_disponibilidad_turno(self, data: dict, medico_id: int, fecha: str, hora: str) -> bool:
    """
    Verifica si hay disponibilidad para un médico en una fecha y hora específicas.
    
    Esta es la función clave para la sincronización entre turnos virtuales y físicos.
    Valida que no exista un turno en el mismo horario, independientemente del origen.
    """
    for turno in data["turnos"]:
        if (int(turno["medico_id"]) == int(medico_id) 
            and turno["fecha"] == fecha 
            and turno["hora"] == hora
            and turno["estado"] in {"PENDIENTE", "CONFIRMADO"}):
            return False  # No hay disponibilidad, el horario está ocupado
    return True  # Hay disponibilidad
```

### 2. Prevención de Turnos Duplicados por Paciente

Se implementó validación para evitar que un paciente tenga múltiples turnos en el mismo horario.

**Método**: `_verificar_turno_duplicado_paciente(data, paciente_id, fecha, hora)`

```python
def _verificar_turno_duplicado_paciente(self, data: dict, paciente_id: int, fecha: str, hora: str) -> bool:
    """
    Verifica si el paciente ya tiene un turno en la misma fecha y hora.
    """
    for turno in data["turnos"]:
        if (int(turno["paciente_id"]) == int(paciente_id) 
            and turno["fecha"] == fecha 
            and turno["hora"] == hora
            and turno["estado"] in {"PENDIENTE", "CONFIRMADO"}):
            return True
    return False
```

### 3. Modificación del Método create_turno

El método `create_turno` ahora incluye validación de disponibilidad antes de crear el turno:

```python
def create_turno(self, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Crea un nuevo turno con validación de disponibilidad en tiempo real.
    
    Este método implementa el sistema de sincronización entre turnos virtuales
    y físicos, similar a un sistema de venta de boletos de avión: cuando alguien
    reserva un turno, el cupo se bloquea inmediatamente para evitar double-booking.
    """
    # ... validaciones de médico y paciente ...
    
    # Validar disponibilidad en tiempo real (sincronización virtual/físico)
    if not self._verificar_disponibilidad_turno(data, medico["id"], payload["fecha"], payload["hora"]):
        raise ValueError("No hay disponibilidad para este médico en la fecha y hora seleccionada. El horario ya está reservado.")
    
    # Verificar si el paciente ya tiene un turno en el mismo horario
    if self._verificar_turno_duplicado_paciente(data, paciente["id"], payload["fecha"], payload["hora"]):
        raise ValueError("El paciente ya tiene un turno reservado en esta fecha y hora.")
    
    # ... crear turno con origen VIRTUAL o FISICO ...
```

### 4. Nuevo Campo: Origen del Turno

Se agregó el campo `origen` a los turnos para distinguir entre reservas virtuales y físicas:

- `VIRTUAL`: Reserva realizada a través de la plataforma web
- `FISICO`: Reserva realizada presencialmente en el hospital

```python
turno = {
    # ... otros campos ...
    "origen": payload.get("origen", "VIRTUAL"),  # VIRTUAL o FISICO
    "fecha_creacion": self._now(),
}
```

### 5. Método para Verificar Disponibilidad Específica

Se implementó un método para que el personal del hospital pueda verificar disponibilidad antes de hacer una reserva física.

**Método**: `verificar_disponibilidad_especifica(medico_id, fecha, hora)`

```python
def verificar_disponibilidad_especifica(self, medico_id: int, fecha: str, hora: str) -> dict[str, Any]:
    """
    Verifica si hay disponibilidad específica para un médico en una fecha y hora.
    
    Este método es usado por el personal del hospital para verificar si un horario
    está disponible antes de hacer una reserva física.
    """
    with self._lock:
        data = self.read()
        medico = self._find(data["medicos"], int(medico_id))
        if medico is None:
            return {"disponible": False, "mensaje": "El médico no existe"}
        
        disponible = self._verificar_disponibilidad_turno(data, medico["id"], fecha, hora)
        if disponible:
            return {
                "disponible": True,
                "mensaje": "El horario está disponible",
                "medico": self._enrich_medico(data, medico)
            }
        else:
            return {
                "disponible": False,
                "mensaje": "El horario ya está reservado por otro paciente"
            }
```

### 6. Método para Crear Turnos Físicos

Se implementó un método específico para crear turnos desde reservas físicas en el hospital.

**Método**: `create_turno_fisico(payload)`

```python
def create_turno_fisico(self, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Crea un turno desde una reserva física en el hospital.
    
    Este método es usado por el personal del hospital cuando un paciente
    se presenta presencialmente y quiere reservar un turno.
    """
    payload["origen"] = "FISICO"  # Marcar como reserva física
    return self.create_turno(payload)
```

### 7. Endpoints de API

Se agregaron dos nuevos endpoints al servidor:

#### Verificar Disponibilidad Específica

```http
POST /api/turnos/verificar-disponibilidad
Content-Type: application/json

{
  "medico_id": 1,
  "fecha": "2026-06-20",
  "hora": "09:30"
}
```

**Respuesta:**
```json
{
  "disponible": true,
  "mensaje": "El horario está disponible",
  "medico": {
    "id": 1,
    "nombre": "Dr. Juan Pérez",
    "especialidad": "Cardiología"
  }
}
```

#### Crear Turno Físico

```http
POST /api/turnos/crear-fisico
Content-Type: application/json

{
  "paciente_id": 1,
  "medico_id": 1,
  "fecha": "2026-06-20",
  "hora": "09:30",
  "motivo": "Dolor de pecho"
}
```

**Respuesta:**
```json
{
  "id": 123,
  "paciente_id": 1,
  "medico_id": 1,
  "fecha": "2026-06-20",
  "hora": "09:30",
  "estado": "PENDIENTE",
  "origen": "FISICO",
  "fecha_creacion": "2026-06-09T16:30:00"
}
```

## Flujo de Sincronización

### Reserva Virtual (Plataforma Web)

1. Paciente selecciona médico, fecha y hora en la plataforma web
2. Sistema verifica disponibilidad en tiempo real
3. Si hay disponibilidad, se crea el turno con `origen: "VIRTUAL"`
4. El cupo queda bloqueado para reservas físicas
5. Si no hay disponibilidad, se muestra mensaje de error

### Reserva Física (Hospital)

1. Paciente se presenta presencialmente en el hospital
2. Personal del hospital verifica disponibilidad usando `/api/turnos/verificar-disponibilidad`
3. Si hay disponibilidad, se crea el turno usando `/api/turnos/crear-fisico`
4. El turno se crea con `origen: "FISICO"`
5. Si no hay disponibilidad (ya reservado virtualmente), se informa al paciente

## Ventajas de la Solución

1. **Sincronización en tiempo real**: Ambos canales (virtual y físico) consultan la misma fuente de verdad
2. **Prevención de double-booking**: No se pueden reservar turnos duplicados en el mismo horario
3. **Trazabilidad**: El campo `origen` permite identificar cómo se reservó cada turno
4. **Flexibilidad**: El personal del hospital puede verificar disponibilidad antes de reservar
5. **Experiencia de usuario**: Los pacientes reciben feedback inmediato sobre disponibilidad
6. **Similar a sistemas de boletos**: Funciona como un sistema de venta de boletos de avión

## Próximas Mejoras

1. **Sistema de liberación de turnos no confirmados**: Liberar automáticamente turnos que no se confirmaron en X minutos
2. **Notificaciones en tiempo real**: Alertar al personal del hospital cuando se reserva un turno virtual
3. **Sistema de espera (waitlist)**: Permitir que pacientes se inscriban en lista de espera para horarios ocupados
4. **Validación de horarios de agenda**: Verificar que el horario solicitado esté dentro de la agenda del médico
5. **Sistema de bloqueo temporal**: Bloquear temporalmente un horario mientras un paciente completa el proceso de reserva

## Ejemplo de Uso

### Reserva Virtual (Plataforma Web)

```javascript
// Paciente reserva turno desde la plataforma web
fetch('/api/turnos', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    paciente_id: 1,
    medico_id: 1,
    fecha: '2026-06-20',
    hora: '09:30',
    motivo: 'Dolor de pecho'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Turno reservado:', data);
  // El turno se crea con origen: "VIRTUAL"
});
```

### Reserva Física (Hospital)

```javascript
// Personal del hospital verifica disponibilidad
fetch('/api/turnos/verificar-disponibilidad', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    medico_id: 1,
    fecha: '2026-06-20',
    hora: '09:30'
  })
})
.then(response => response.json())
.then(data => {
  if (data.disponible) {
    // Crear turno físico
    return fetch('/api/turnos/crear-fisico', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        paciente_id: 2,
        medico_id: 1,
        fecha: '2026-06-20',
        hora: '09:30',
        motivo: 'Consulta de rutina'
      })
    });
  } else {
    console.log('Horario no disponible:', data.mensaje);
  }
});
```

## Conclusión

Esta solución resuelve el problema de sincronización entre turnos virtuales y físicos implementando un sistema de gestión de cupos en tiempo real, similar a un sistema de venta de boletos de avión. Cuando alguien reserva un turno (virtual o físicamente), el cupo se bloquea inmediatamente para evitar conflictos, asegurando que ambos canales estén sincronizados y que no haya problemas entre pacientes que reservan virtualmente y pacientes que se presentan físicamente.
