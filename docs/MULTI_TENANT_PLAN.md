Plan para modo Multi-Tenant (vender por hospital)

Objetivo

Permitir que Salud Chilecito sea desplegado para múltiples instituciones (tenants), de forma que cada hospital/clinica tenga su propia vista, configuración y datos. El enfoque inicial será single-tenant por instancia con soporte para identificación por subdominio/slug — después pasamos a multi-tenant con aislamiento en la BD.

Fases propuestas

Fase 1 — Identificación y vista por centro (COMPLETADO PARCIALMENTE)

- Detectar el centro por `centro_id` query param o por `slug`/host (subdominio).
- Frontend: filtro por centro y persistencia (se implementó en la UI).
- Tests: unitarios para filtrado (implementados).

Fase 2 — Configuración por centro (impar a multi-tenant)

- Añadir tabla/config en Oracle para `centros_config` con campos: `centro_id`, `slug`, `dominio`, `branding_name`, `branding_logo`, `tarifas_override`.
- Endpoint admin para actualizar configuración de un centro.

Fase 3 — Autenticación y roles por centro

- Añadir usuarios admins por centro (rol `admin_centro`) y autenticación básica (JWT) para la API administrativa.
- Implementar página de login para panel admin.

Fase 4 — Aislamiento (opcional: multi-tenant en la misma instancia)

- En Oracle: añadir columna `centro_id` a tablas relevantes y forzar filtros en consultas DAO.
- Alternativa (más aislamiento): usar schemas por tenant o bases de datos separadas y un config layer que rote DSNs.

Fase 5 — Onboarding y scripts

- Script `scripts/create_tenant.sh` para crear entrada en SQL, tablespaces y usuarios si se necesita más aislamiento.

Entrega mínima viable (MVP)

1. Endpoints que respeten `centro_id`/slug y devuelvan solo datos del centro.
2. Panel admin simple para editar `branding_name` y `tarifas_override` por centro.
3. Documentación y script para migrar datos si se elige aislar por schema.

Estimación de trabajo

- Fase 1: completada parcialmente (2-4 horas para pulir y cubrir casos). Ya están hechos: filtro API y UI.
- Fase 2: 8-16 horas (modelado DB + endpoints admin + UI simple).
- Fase 3: 8-12 horas (autenticación + roles + tests).
- Fase 4: 16-40 horas (depende de la estrategia: schema vs same-db).

Siguiente paso recomendable: implementar la Fase 2 (config por centro) y agregar endpoints administrativos y tests. ¿Lo hago ahora?
