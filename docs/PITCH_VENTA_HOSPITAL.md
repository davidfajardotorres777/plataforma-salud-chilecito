Pitch comercial y guía rápida para vender Salud Chilecito a un hospital

Resumen (elevator pitch)

- Salud Chilecito es una solución de gestión de turnos y pacientes que puede
  instalarse por centro/hospital. Ofrecemos una entrega llave en mano: la
  clínica compra la instancia y el hospital usa su propio subdominio/slug para
  acceder a su sistema personalizado.

Beneficios clave

- Rápida adopción: demo web y chatbot para operar sin instalar base de datos.
- Integración con HIS: endpoints y adaptadores para sincronizar agendas y
  pacientes (ver docs/INTEGRACION_HOSPITAL.md).
- Control de branding y tarifas por centro (plan multi-tenant).

Qué entregamos

1. Instalación del software en servidor del hospital (o cloud privado).
2. Adaptador de integración con HIS (webhooks o job de importación).
3. Onboarding: carga de medicos, agendas y capacitación para secretarias.

Pasos técnicos rápidos (MVP)

1. Crear el centro en Salud Chilecito (POST /api/centros).
2. Cargar medicos y especialidades.
3. Importar agendas via POST /api/agendas/import (CSV -> JSON adaptado) o
   configurar webhooks desde el HIS que llamen a /api/agendas.
4. Probar reservas desde la UI o via POST /api/turnos.

Demostración de uso (ejemplos)

- Obtener disponibilidades de un hospital:
  GET /api/disponibilidad?centro_id=1

- Importar agendas en batch (POST):
  POST /api/agendas/import  -> body: [ { medico_id, dia_semana, hora_inicio, ... }, ... ]

- Calcular precio estimado para un motivo:
  POST /api/calcular_precio -> body: { especialidad_id: 3, motivo: "dolor de pecho" }

Siguiente paso sugerido

- Puedo preparar un script de import (CSV -> JSON) y materiales de venta
  (presentación y demo script) para mostrar al hospital. Dime si quieres
  que genere un paquete de entrega.
