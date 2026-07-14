-- Scripts SQL de ejemplo para la plataforma Salud Chilecito
-- Contienen DDL mínimo para pruebas y demos

-- Tabla centros
CREATE TABLE centros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    direccion TEXT,
    distrito VARCHAR(100),
    tipo VARCHAR(50),
    telefono VARCHAR(50),
    email VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla pacientes
CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(50),
    fecha_nacimiento DATE,
    obra_social VARCHAR(255),
    distrito VARCHAR(100),
    fecha_alta TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nota: estos scripts son ejemplos para documentación y pruebas; en producción usar DDL adaptado al RDBMS elegido.
