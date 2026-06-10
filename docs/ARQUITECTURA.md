# Arquitectura de Salud Chilecito

## Componentes

```mermaid
flowchart TD
    A[Usuario o administracion] --> B[Aplicacion Salud Chilecito]
    A --> K[Notebook de demostracion]
    K --> L[DAO Python]
    L --> D
    B --> C[DAO Python]
    C --> D[Oracle XE]
    D --> E[(tbs_salud_data)]
    D --> F[(tbs_salud_idx)]
    D --> G[FRA 3GB]
```

## Decisiones principales

- Oracle es la base relacional principal del proyecto.
- La plataforma grafica es la entrada principal del proyecto web local.
- Los datos transaccionales viven en tablas normalizadas.
- Los documentos clinicos pueden guardarse como BLOB o por URL externa.
- Los indices se separan en `tbs_salud_idx` para cumplir el criterio fisico.
- El esquema propietario es `salud`; los usuarios de aplicacion reciben roles.

## Migracion desde la idea NoSQL

| Idea original | Modelo Oracle |
|---|---|
| Coleccion de centros | Tabla `centro_salud` |
| Coleccion de medicos | Tabla `medico` |
| Documento paciente | Tabla `paciente` |
| Agenda embebida por medico | Tabla `agenda_medico` |
| Turnos con datos relacionados | Tabla `turno` con FK a paciente, medico y centro |
| Adjuntos externos | Tabla `documento_paciente` con BLOB o URL |
