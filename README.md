# 🏥 Salud Chilecito

> **Plataforma integral de gestión de turnos y datos clínicos para el departamento de Chilecito y sus distritos.**

![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-blue)
![Arquitectura](https://img.shields.io/badge/Arquitectura-Microservicios-orange)
![Base_de_Datos](https://img.shields.io/badge/DB-Políglota-success)

## 📋 Descripción del Proyecto

**Salud Chilecito** busca digitalizar y descentralizar el acceso a la atención médica en Chilecito, Nonogasta, Sañogasta y Vichigasta[cite: 236, 237]. [cite_start]La plataforma conecta a centros de salud públicos y privados con los ciudadanos a través de un ecosistema digital, eliminando las barreras geográficas y optimizando los recursos del sistema sanitario local[cite: 9, 10, 237].

---

## ⚠️ Problemática Local vs. Nuestra Solución

[cite_start]El sistema de salud actual en nuestra región sufre de deficiencias estructurales que esta plataforma viene a resolver[cite: 239]:

| Problema Actual | Solución Salud Chilecito |
| :--- | :--- |
| [cite_start]**Saturación física:** Filas desde las 5 AM sin garantía de turno[cite: 7, 240]. | [cite_start]**Gestión 24/7:** Reserva instantánea desde la app o web[cite: 16, 17]. |
| [cite_start]**Falta de información:** Desconocimiento de especialistas disponibles[cite: 8, 240]. | [cite_start]**Registro Centralizado:** Perfiles gestionables por cada clínica[cite: 93]. |
| [cite_start]**Desperdicio de recursos:** Alto ausentismo y huecos en agendas[cite: 10, 240]. | [cite_start]**Recordatorios:** Alertas automáticas vía SMS/Push[cite: 18, 19]. |
| [cite_start]**Incertidumbre económica:** Costos ocultos hasta llegar a recepción[cite: 11, 240]. | [cite_start]**Transparencia:** Visualización de costos y copagos previos a la reserva[cite: 20, 21]. |

---

## 🗄️ Arquitectura de Bases de Datos (Modelo Políglota)

[cite_start]Para manejar la variabilidad de los datos médicos y garantizar tiempos de respuesta en milisegundos, el sistema implementa persistencia políglota[cite: 31, 269]:

### 1. MongoDB (Core - NoSQL Documental)
[cite_start]Núcleo del sistema para perfiles de clínicas, médicos y turnos[cite: 34, 35]. [cite_start]Se eligió por su esquema flexible frente a datos médicos variables[cite: 36, 136].
* **Bucket Pattern:** Aplicado en la agenda médica. [cite_start]Agrupa los turnos por rangos diarios para evitar el antipatrón de *unbounded arrays*, manteniendo los documentos pequeños y optimizando las consultas [cite: 46-49, 138-140].
* **Extended Reference Pattern:** Aplicado en los turnos. [cite_start]Incrusta solo la información vital (nombre, especialidad) para evitar `Joins` costosos y mejorar los tiempos de respuesta del frontend [cite: 50-53, 141].

### 2. Redis (Caché en RAM)
[cite_start]Almacenamiento Clave-Valor para servir la disponibilidad de turnos en tiempo real, sesiones activas y listados estáticos, reduciendo la carga operativa del motor principal[cite: 39, 40, 144, 145].

---

## ⚙️ Configuración del Entorno Local (Data Access Objects)

Para ejecutar el proyecto y los scripts de acceso a datos (DAO), es necesario configurar el entorno de desarrollo siguiendo estos pasos.

### Requisitos Previos
* IDE o Editor de código
* Python 3.12
* Actualizar pip: `pip install --upgrade pip`

### Inicialización de Base de Datos
* Ejecutar el script SQL proporcionado: `[dbscripts](dbscripts.sql)`

### Creación y Activación del Entorno Virtual
```bash
# Crear el entorno virtual
python -m venv ./venv

# Activar el entorno virtual (Linux/Mac)
source ./venv/bin/activate
