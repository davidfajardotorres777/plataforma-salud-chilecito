# 🏥 Salud Chilecito

> **Plataforma integral de gestión de turnos y datos clínicos para el departamento de Chilecito y sus distritos.**  
> Trabajo Integrador — Bases de Datos · Ingeniería en Sistemas · Universidad Nacional de Chilecito · 2026

![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-blue?style=flat-square)
![Arquitectura](https://img.shields.io/badge/Arquitectura-Microservicios-orange?style=flat-square)
![BD](https://img.shields.io/badge/DB-Modelo_Políglota-green?style=flat-square)
![Node](https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=node.js)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-47A248?style=flat-square&logo=mongodb)
![Redis](https://img.shields.io/badge/Redis-7.2-DC382D?style=flat-square&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)

---

## 📋 Índice

- [El problema](#-el-problema)
- [La solución](#-la-solución)
- [Bases de datos](#-arquitectura-de-bases-de-datos-modelo-políglota)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso de la API](#-uso-de-la-api)
- [Patrones de diseño](#-patrones-de-diseño-mongodb)
- [Escalabilidad](#-estrategia-de-escalabilidad)
- [Monetización](#-modelo-de-monetización)
- [Autor](#-autor)

---

## 🔴 El problema

En el departamento de Chilecito (La Rioja), el sistema de salud presenta deficiencias estructurales que afectan especialmente a la población de menores recursos y a los habitantes de los distritos periféricos (Nonogasta, Sañogasta, Vichigasta):

| Problema | Impacto en la comunidad |
| :--- | :--- |
| **Saturación física** | Pacientes que hacen fila desde las 5 AM sin garantía de obtener turno. |
| **Falta de información** | El ciudadano no sabe qué especialistas están disponibles sin ir personalmente. |
| **Desperdicio de recursos** | Alto ausentismo; médicos con huecos en la agenda sin poder cubrirlos. |
| **Incertidumbre económica** | El costo de la consulta se desconoce hasta llegar a la administración. |
| **Barreras geográficas** | Habitantes de distritos alejados deben trasladarse solo para pedir un turno. |

---

## ✅ La solución

**Salud Chilecito** es una plataforma web y móvil que digitaliza la gestión de turnos médicos, conectando a los centros de salud con los ciudadanos de forma directa.

| Solución | Descripción |
| :--- | :--- |
| **Reserva 24/7** | El usuario visualiza la agenda real de médicos y reserva desde su celular, sin trasladarse. |
| **Registro centralizado** | Cada clínica u hospital gestiona su propio perfil: especialidades, médicos, horarios y costos. |
| **Transparencia de costos** | Visualización del monto de la consulta y el copago de la obra social antes de confirmar. |
| **Recordatorios automáticos** | Alertas vía app/SMS 24 horas antes del turno para reducir el ausentismo. |
| **Historial del paciente** | Turnos pasados, documentos adjuntos (órdenes médicas, estudios) y estado de cada consulta. |

---

## 🗄️ Arquitectura de Bases de Datos (Modelo Políglota)

El proyecto adopta **persistencia políglota**: distintas bases de datos especializadas según el tipo de dato y el patrón de acceso requerido.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MODELO POLÍGLOTA                            │
│                                                                     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌────────────────┐   │
│  │    MongoDB      │    │     Redis       │    │  Firebase /    │   │
│  │  (Documental)   │    │  (Key-Value)    │    │    AWS S3      │   │
│  │                 │    │                 │    │  (Archivos)    │   │
│  │ • Clínicas      │    │ • Slots libres  │    │ • PDFs         │   │
│  │ • Médicos       │◄──►│ • Sesiones      │    │ • Imágenes     │   │
│  │ • Pacientes     │    │ • Especialidades│    │ • Estudios     │   │
│  │ • Turnos        │    │                 │    │                │   │
│  │ • Agenda        │    │ TTL: 5min–24hs  │    │ MongoDB guarda │   │
│  └─────────────────┘    └─────────────────┘    │ solo la URL    │   │
│                                                 └────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### 1. 🍃 MongoDB — Base de Datos Principal

**Tipo:** NoSQL Documental  
**Justificación:** Los datos de salud son naturalmente variables. No todas las clínicas tienen los mismos campos ni los mismos horarios. MongoDB permite esquemas flexibles que evolucionan sin rediseñar toda la estructura. A diferencia de una base relacional, no requiere ALTER TABLE para agregar una nueva especialidad o un nuevo campo de obra social.

Se aplican dos patrones de diseño avanzados (detallados en la [sección de patrones](#-patrones-de-diseño-mongodb)).

### 2. ⚡ Redis — Caché en Memoria

**Tipo:** Key-Value en RAM  
**Justificación:** La disponibilidad de turnos se consulta miles de veces por día. Redis los sirve desde la memoria RAM en milisegundos, sin impactar a MongoDB en cada request.

| Dato cacheado | TTL | Razón |
| :--- | :---: | :--- |
| Slots disponibles del día | 5 min | Cambia con cada reserva; se invalida automáticamente |
| Sesión de usuario autenticado | 1 hora | Seguridad |
| Especialidades por clínica | 24 hs | Dato estático; rara vez cambia |

### 3. 📁 Firebase Storage / AWS S3 — Almacenamiento de Archivos

**Tipo:** Object Storage en la nube  
**Justificación:** No tiene sentido guardar archivos binarios dentro de documentos MongoDB: haría los documentos enormes y lentos. Con S3 cada archivo tiene su propia URL y MongoDB solo guarda el enlace.

```json
// En MongoDB solo se guarda la referencia, nunca el binario:
{
  "documentos_adjuntos": [
    "https://storage.saludchilecito.com/ordenes/ord_001.pdf"
  ]
}
```

---

## 📐 Patrones de Diseño MongoDB

### 🪣 Bucket Pattern → colección `agenda_medico`

**Problema que resuelve:** el antipatrón *Unbounded Arrays*. Si todos los turnos históricos de un médico vivieran en un único array dentro de su documento, ese array crecería infinitamente, superando el límite de 16 MB del documento BSON.

```
❌ ANTIPATRÓN (NO hacer):
{
  "_id": ObjectId,
  "nombre": "Dra. González",
  "turnos": [
    // ... miles de turnos históricos que crecen sin límite
    // el documento eventualmente supera los 16 MB y colapsa
  ]
}

✅ BUCKET PATTERN (solución aplicada):
// Un documento por médico por día.
// Cuando el día termina o el bucket se llena, se crea uno nuevo.
{
  "id_medico": ObjectId,
  "fecha": ISODate("2026-05-10"),
  "slots_count": 8,
  "slots_ocupados": 3,
  "slots": [
    { "hora": "09:00", "estado": "disponible" },
    { "hora": "09:30", "estado": "reservado", "id_turno": ObjectId },
    { "hora": "10:00", "estado": "disponible" }
    // máximo 20 slots por documento
  ]
}
```

> **Analogía de clase:** igual al caso del sensor IoT de temperatura. En lugar de 1 documento por lectura (millones de docs) o 1 array infinito, se agrupan los datos en períodos controlados.

---

### 🔗 Extended Reference Pattern → colección `turnos`

**Problema que resuelve:** la necesidad de mostrar nombre del paciente + médico + clínica en cada turno sin hacer 3 lookups adicionales a MongoDB.

```
❌ SIN PATRÓN (hace 3 consultas extra por cada turno):
{
  "id_paciente": ObjectId,   // hay que consultar pacientes
  "id_medico":   ObjectId,   // hay que consultar medicos
  "id_centro":   ObjectId    // hay que consultar centros_salud
}

✅ EXTENDED REFERENCE (datos esenciales embebidos):
{
  "fecha": ISODate("2026-05-10T09:30:00Z"),
  "estado": "pendiente",
  "paciente": {
    "id":       ObjectId,                 // fuente de verdad
    "nombre":   "Juan Pérez",             // solo lo esencial
    "telefono": "+54 9 3825 111222",
    "dni":      "32456789"
  },
  "medico": {
    "id":          ObjectId,
    "nombre":      "Dra. María González",
    "especialidad":"Cardiología"
  },
  "centro": {
    "id":       ObjectId,
    "nombre":   "Clínica San Juan",
    "direccion":"Pelagio Luna 350, Chilecito"
  }
}
```

> **Concepto clave (discutido en clase):** al guardar solo el `id` como fuente de verdad, cuando un dato central cambia se actualiza en UN solo lugar. No hay riesgo de inconsistencias entre distintas partes del sistema.

---

## 🗂️ Estructura del Proyecto

```
salud-chilecito/
│
├── src/
│   ├── config/
│   │   └── database.js          # Conexión MongoDB + Redis; TTL definidos
│   │
│   ├── models/                  # Colecciones MongoDB (Mongoose)
│   │   ├── AgendaMedico.js      # ← Bucket Pattern aplicado
│   │   ├── Turno.js             # ← Extended Reference Pattern aplicado
│   │   ├── CentroSalud.js       # Extended Reference en especialidades
│   │   ├── Medico.js            # Extended Reference en especialidad
│   │   ├── Paciente.js          # Fuente de verdad del paciente
│   │   └── Especialidad.js      # Catálogo centralizado
│   │
│   ├── routes/
│   │   ├── turnos.js            # POST /reservar · GET /disponibles · etc.
│   │   └── centros.js           # GET /centros · POST /centros · etc.
│   │
│   ├── services/
│   │   └── turnoService.js      # Lógica: Bucket + Redis cache + Extended Reference
│   │
│   ├── seeds/
│   │   └── index.js             # Datos de prueba: Chilecito, Nonogasta, etc.
│   │
│   └── index.js                 # Punto de entrada del servidor
│
├── docker-compose.yml           # MongoDB 7.0 + Redis 7.2 en contenedores
├── .env.example                 # Variables de entorno de ejemplo
├── .gitignore
├── package.json
└── README.md
```

---

## 🚀 Instalación

### Requisitos previos

Verificá que estén instalados antes de continuar:

```bash
node --version    # debe mostrar v18 o superior
docker ps         # debe mostrar una tabla (aunque vacía)
git --version     # debe mostrar la versión instalada
```

### 1. Clonar el repositorio

```bash
git clone https://github.com/AlesandroFajardo/salud-chilecito.git
cd salud-chilecito
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

El archivo `.env` resultante contiene los valores por defecto para desarrollo local y no necesita modificarse para la primera prueba:

```env
MONGO_URI=mongodb://localhost:27017/salud_chilecito
REDIS_HOST=localhost
REDIS_PORT=6379
PORT=3000
NODE_ENV=development
```

> El archivo `.env` está excluido por `.gitignore` y nunca se sube al repositorio.

### 3. Levantar las bases de datos con Docker

```bash
docker-compose up -d
```

Verificar que los contenedores estén corriendo:

```bash
docker ps
# Debe aparecer salud_chilecito_mongo y salud_chilecito_redis con STATUS "Up"
```

### 4. Instalar dependencias

```bash
npm install
```

### 5. Cargar datos de prueba

```bash
npm run seed
```

Resultado esperado:

```
✅ MongoDB conectado → mongodb://localhost:27017/salud_chilecito
🗑️  Colecciones limpiadas
✅ Especialidades creadas
✅ Centros de salud creados
✅ Médicos creados
✅ Pacientes creados
✅ Agendas del día creadas (Bucket Pattern)

🎉 Seed completado. Ya podés probar la API.
```

### 6. Iniciar el servidor

```bash
npm run dev
```

La API queda disponible en `http://localhost:3000`.

---

## 🔗 Uso de la API

### Información del proyecto

```http
GET http://localhost:3000/
```

```json
{
  "proyecto": "Salud Chilecito",
  "version": "1.0.0",
  "bases_de_datos": {
    "principal": "MongoDB — Bucket + Extended Reference Pattern",
    "cache": "Redis — slots, sesiones, especialidades",
    "archivos": "Firebase Storage / AWS S3"
  }
}
```

---

### Centros de Salud

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/centros` | Lista todos los centros activos *(con caché Redis 24 hs)* |
| `GET` | `/api/centros/:id` | Detalle de un centro |
| `POST` | `/api/centros` | Registrar nuevo centro |
| `GET` | `/api/centros/:id/medicos` | Médicos de un centro |

**Ejemplo — Registrar un centro:**

```bash
curl -X POST http://localhost:3000/api/centros \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Clínica San Juan",
    "tipo": "Privado",
    "direccion": {
      "calle": "Pelagio Luna 350",
      "distrito": "Chilecito"
    },
    "telefono": "+54 3825 123456",
    "especialidades": [
      { "id_especialidad": "<ObjectId>", "nombre": "Cardiología" }
    ],
    "plan_suscripcion": "premium"
  }'
```

---

### Turnos

| Método | Ruta | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/turnos/disponibles/:idMedico/:fecha` | Slots libres del día *(Bucket Pattern + Redis cache)* |
| `POST` | `/api/turnos/reservar` | Reservar un turno |
| `PUT` | `/api/turnos/:id/cancelar` | Cancelar un turno |
| `GET` | `/api/turnos/paciente/:idPaciente` | Historial del paciente |

**Ejemplo — Ver slots disponibles:**

```bash
curl http://localhost:3000/api/turnos/disponibles/<idMedico>/2026-05-10
```

```json
{
  "ok": true,
  "data": [
    { "hora": "09:00", "estado": "disponible" },
    { "hora": "10:00", "estado": "disponible" },
    { "hora": "14:00", "estado": "disponible" }
  ]
}
```

**Ejemplo — Reservar turno:**

```bash
curl -X POST http://localhost:3000/api/turnos/reservar \
  -H "Content-Type: application/json" \
  -d '{
    "idPaciente": "<ObjectId>",
    "idMedico":   "<ObjectId>",
    "idCentro":   "<ObjectId>",
    "fecha":      "2026-05-10",
    "hora":       "09:00"
  }'
```

```json
{
  "ok": true,
  "data": {
    "_id": "<ObjectId>",
    "fecha": "2026-05-10T09:00:00.000Z",
    "estado": "pendiente",
    "paciente": { "nombre": "Juan Pérez", "dni": "32456789" },
    "medico":   { "nombre": "Dra. María González", "especialidad": "Cardiología" },
    "centro":   { "nombre": "Clínica San Juan", "direccion": "Pelagio Luna 350, Chilecito" }
  }
}
```

---

## 📈 Estrategia de Escalabilidad

El sistema fue diseñado para crecer en tres etapas sin reescritura:

| Etapa | Alcance | Tecnología clave |
| :---: | :--- | :--- |
| **1 — Local** | Chilecito y distritos. Piloto en una clínica. | Un VPS · MongoDB single node · validación del producto. |
| **2 — Provincial** | La Rioja, Mendoza, Córdoba... | Sharding en MongoDB por región · Load Balancer · múltiples servidores. |
| **3 — Global** | Latinoamérica, EE.UU., Europa. | Microservicios independientes · AWS/GCP multi-región · CDN. |

El diseño en **microservicios** permite escalar solo el componente bajo presión. Por ejemplo: si el lunes hay un pico de reservas, se escala únicamente el microservicio de Turnos sin afectar el resto del sistema.

---

## 💰 Modelo de Monetización

El proyecto utiliza un modelo mixto adaptado a la realidad económica de la región:

| Fuente | Descripción |
| :--- | :--- |
| **Plan Premium (B2B)** | Clínicas privadas — $35.000 ARS/mes. Hospitales públicos: **gratuitos** como estrategia de adopción. |
| **Comisión por transacción** | 2–3% en pagos online. Escalable: a más turnos pagados, más ingreso pasivo. |
| **Publicidad local segmentada** | Farmacias, laboratorios y ópticas de Chilecito como anuncios contextuales útiles. |
| **Datos estadísticos anonimizados** | Venta de métricas agregadas (nunca datos personales) a obras sociales y al Ministerio de Salud. |

---

## 🧩 Colecciones MongoDB — Resumen

| Colección | Patrón aplicado | Qué almacena |
| :--- | :--- | :--- |
| `centros_salud` | Extended Reference (especialidades) | Perfil de cada clínica u hospital |
| `medicos` | Extended Reference (especialidad) | Datos del médico y su especialidad |
| `agenda_medico` | **Bucket Pattern** | Slots de turnos agrupados por médico/día |
| `turnos` | **Extended Reference** | Reserva con datos esenciales embebidos |
| `pacientes` | — | Perfil completo del paciente (fuente de verdad) |
| `especialidades` | — | Catálogo centralizado de especialidades |

---

## 👤 Autor

**Alesandro David Fajardo**  
Ingeniería en Sistemas — Universidad Nacional de Chilecito (UNdeC)  
Año: 2026

---

*Bases de Datos · Diseño y Arquitectura · UNdeC 2026*
