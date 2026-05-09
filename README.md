# 🏥 Salud Chilecito

> **Plataforma integral de gestión de turnos y datos clínicos para el departamento de Chilecito y sus distritos.**

![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-blue)
![Arquitectura](https://img.shields.io/badge/Arquitectura-Microservicios-orange)
![Base_de_Datos](https://img.shields.io/badge/DB-Políglota-success)

## 📋 Descripción del Proyecto

**Salud Chilecito** busca digitalizar y descentralizar el acceso a la atención médica en Chilecito, Nonogasta, Sañogasta y Vichigasta. La plataforma conecta a centros de salud públicos y privados con los ciudadanos a través de un ecosistema digital, eliminando las barreras geográficas y optimizando los recursos del sistema sanitario local.

---

## ⚠️ Problemática Local vs. Nuestra Solución

El sistema de salud actual en nuestra región sufre de deficiencias estructurales que esta plataforma viene a resolver:

| Problema Actual | Solución Salud Chilecito |
| :--- | :--- |
| **Saturación física:** Filas desde las 5 AM sin garantía de turno. | **Gestión 24/7:** Reserva instantánea desde la app o web. |
| **Falta de información:** Desconocimiento de especialistas disponibles. | **Registro Centralizado:** Perfiles gestionables por cada clínica. |
| **Desperdicio de recursos:** Alto ausentismo y huecos en agendas. | **Recordatorios:** Alertas automáticas vía SMS/Push. |
| **Incertidumbre económica:** Costos ocultos hasta llegar a recepción. | **Transparencia:** Visualización de costos y copagos previos a la reserva. |

---

## 🗄️ Arquitectura de Bases de Datos (Modelo Políglota)

Para manejar la variabilidad de los datos médicos y garantizar tiempos de respuesta en milisegundos, el sistema implementa persistencia políglota:

### 1. MongoDB (Core - NoSQL Documental)
Núcleo del sistema para perfiles de clínicas, médicos y turnos. Se eligió por su esquema flexible frente a datos médicos variables.
* **Bucket Pattern:** Aplicado en la agenda médica. Agrupa los turnos por rangos diarios para evitar el antipatrón de *unbounded arrays*, manteniendo los documentos pequeños y optimizando las consultas.
* **Extended Reference Pattern:** Aplicado en los turnos. Incrusta solo la información vital (nombre, especialidad) para evitar `Joins` costosos y mejorar los tiempos de respuesta del frontend.

### 2. Redis (Caché en RAM)
Almacenamiento Clave-Valor para servir la disponibilidad de turnos en tiempo real, sesiones activas y listados estáticos, reduciendo la carga operativa del motor principal.

---

## ⚙️ Configuración del Entorno Local (Data Access Objects)

### Before you begin, you’ll need:
* IDE or Text editor
* Python 3.12
* `pip install --upgrade pip`

### Create database schema
* Ejecutar el script `dbscripts.sql`

### Create the virtual environment
```bash
python -m venv ./venv
