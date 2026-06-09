Guia de despliegue rapido por hospital
======================================

Objetivo
--------
Vender e instalar Salud Chilecito en un hospital o clinica privada.
El hospital obtiene su propia instancia con acceso via subdominio o slug.

Requisitos
----------
- Python 3.12+
- Docker (opcional, para Oracle)
- Conexion a internet (para dependencias)

Paso 1: Clonar e instalar
-------------------------

```bash
git clone <repo-url> salud-chilecito-hospital
cd salud-chilecito-hospital
pip install -r requirements.txt
```

Paso 2: Configurar el hospital
------------------------------

Editar `data/demo_seed.json` o usar la API para crear el centro:

```bash
# Iniciar la plataforma
python -m src.webapp.server
```

Crear centro via API:

```bash
curl -X POST http://localhost:8000/api/centros \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Hospital Chilecito",
    "slug": "hospital-chilecito",
    "direccion": "Av. Principal 123",
    "distrito": "Chilecito",
    "telefono": "3825-100000",
    "tipo": "PUBLICO"
  }'
```

Paso 3: Cargar medicos y agendas
---------------------------------

Opcion A: Via interfaz web (panel admin)

1. Abrir http://localhost:8000
2. Ir a "Turnos" -> agregar medicos y agendas manualmente

Opcion B: Via script CSV (recomendado para lots grandes)

Crear archivo CSV `agendas.csv`:

```
medico_id,dia_semana,hora_inicio,hora_fin,duracion_minutos,cupo_diario
1,Lunes,08:00,12:00,30,8
1,Miercoles,08:00,12:00,30,8
1,Viernes,14:00,18:00,30,8
```

Importar:

```bash
python scripts/import_agendas.py --csv agendas.csv
```

Opcion C: Via API directamente

```bash
curl -X POST http://localhost:8000/api/agendas/import \
  -H "Content-Type: application/json" \
  -d '[
    {"medico_id": 1, "dia_semana": "Lunes", "hora_inicio": "08:00", "hora_fin": "12:00", "duracion_minutos": 30, "cupo_diario": 8},
    {"medico_id": 1, "dia_semana": "Miercoles", "hora_inicio": "08:00", "hora_fin": "12:00", "duracion_minutos": 30, "cupo_diario": 8}
  ]'
```

Paso 4: Acceso publico para pacientes
--------------------------------------

Los pacientes acceden a traves de:

  http://localhost:8000/hospital-chilecito

  (donde "hospital-chilecito" es el slug del centro)

La pagina publica muestra:
1. Especialidades disponibles en el hospital
2. Medicos por especialidad con cupos
3. Dias y horarios de atencion
4. Formulario de reserva con calculo de precio

Paso 5: Configuracion de dominio (produccion)
-----------------------------------------------

Para que el hospital tenga su propio dominio:

Opcion A: Subdominio
  hospital-chilecito.saludchilecito.com → configurar DNS CNAME

Opcion B: Dominio propio
  turnos.hospitalchilecito.com → configurar DNS + proxy reverso

En ambos casos, la plataforma detecta el dominio via el header Host
y muestra automaticamente la vista del hospital correcto.

Integracion con HIS del hospital
---------------------------------

Ver docs/INTEGRACION_HOSPITAL.md para detalles completos.

Resumen rapido:
1. El HIS del hospital puede enviar webhooks a /api/agendas
2. O ejecutar un job de sincronizacion con /api/agendas/import
3. Los pacientes reservan desde la pagina publica del hospital
4. Los turnos aparecen en el panel admin y en el HIS

Endpoints de integracion:

  GET  /api/disponibilidad?centro_id=<id>&especialidad_id=<id>
  POST /api/agendas/import (batch de agendas)
  POST /api/calcular_precio (estimar precio por motivo)
  POST /api/turnos (crear turno)
  POST /api/turnos/<id>/estado (cambiar estado)

Comandos utiles
----------------

Iniciar solo la web:
  python -m src.webapp.server

Ejecutar tests:
  python -m pytest -q

Abrir notebook demo:
  python scripts/windows/04_abrir_notebook.ps1  (Windows)
  bash scripts/ubuntu/04_abrir_notebook.sh       (Ubuntu)
