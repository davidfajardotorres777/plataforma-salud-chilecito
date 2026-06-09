-- Datos de prueba para las nuevas funcionalidades
-- Ejecutar conectado como usuario salud

-- Tipos de consulta
INSERT INTO tipo_consulta (nombre, descripcion, duracion_minutos) VALUES 
('Consulta General', 'Consulta de rutina o control', 30),
('Consulta de Urgencia', 'Atencion prioritaria por sintomas agudos', 20),
('Consulta de Seguimiento', 'Control posterior a tratamiento', 20),
('Estudio Complementario', 'Realizacion de estudios diagnosticos', 45),
('Primera Consulta', 'Primera vez con el especialista', 45);

-- Sintomas y su mapeo a especialidades
INSERT INTO sintoma (descripcion, id_especialidad, prioridad) VALUES 
('Dolor de pecho', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Cardiologia'), 'ALTA'),
('Palpitaciones', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Cardiologia'), 'MEDIA'),
('Dificultad para respirar', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Cardiologia'), 'ALTA'),
('Mareos frecuentes', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Cardiologia'), 'MEDIA'),
('Dolor de cabeza intenso', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Clinica Medica'), 'MEDIA'),
('Fiebre alta', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Clinica Medica'), 'MEDIA'),
('Dolor abdominal', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Clinica Medica'), 'MEDIA'),
('Dolor de garganta', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Clinica Medica'), 'BAJA'),
('Dolor de muelas', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Odontologia'), 'MEDIA'),
('Sangrado de encias', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Odontologia'), 'MEDIA'),
('Dolor de rodilla', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Traumatologia'), 'MEDIA'),
('Dolor de espalda', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Traumatologia'), 'MEDIA'),
('Fractura sospechada', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Traumatologia'), 'ALTA'),
('Control ginecologico', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Ginecologia'), 'MEDIA'),
('Dolor pelvico', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Ginecologia'), 'MEDIA'),
('Fiebre en ninos', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Pediatria'), 'ALTA'),
('Dolor de oido en ninos', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Pediatria'), 'MEDIA'),
('Vomitos en ninos', (SELECT id_especialidad FROM especialidad WHERE nombre = 'Pediatria'), 'ALTA');

-- Configuracion del hospital (ejemplo para Hospital Eleazar Herrera Motta)
INSERT INTO configuracion_hospital (nombre_hospital, logo_url, color_primario, color_secundario, mensaje_bienvenida, requiere_derivacion, tiempo_cancelacion_horas, id_centro_principal)
SELECT 'Hospital Eleazar Herrera Motta', NULL, '#0066cc', '#ffffff', 
       'Bienvenido al sistema de turnos online del Hospital Eleazar Herrera Motta. Seleccione sus sintomas para encontrar el especialista adecuado.', 
       'N', 24, id_centro
FROM centro_salud 
WHERE nombre = 'Hospital Eleazar Herrera Motta';

-- Precios por especialidad y tipo de consulta (para clinica privada)
INSERT INTO precio_especialidad (id_centro, id_especialidad, id_tipo_consulta, precio_minimo, precio_maximo, precio_estimado)
SELECT 
    c.id_centro,
    e.id_especialidad,
    tc.id_tipo_consulta,
    CASE 
        WHEN tc.nombre = 'Consulta General' THEN 8000
        WHEN tc.nombre = 'Consulta de Urgencia' THEN 15000
        WHEN tc.nombre = 'Consulta de Seguimiento' THEN 5000
        WHEN tc.nombre = 'Estudio Complementario' THEN 12000
        WHEN tc.nombre = 'Primera Consulta' THEN 10000
    END as precio_minimo,
    CASE 
        WHEN tc.nombre = 'Consulta General' THEN 12000
        WHEN tc.nombre = 'Consulta de Urgencia' THEN 20000
        WHEN tc.nombre = 'Consulta de Seguimiento' THEN 8000
        WHEN tc.nombre = 'Estudio Complementario' THEN 18000
        WHEN tc.nombre = 'Primera Consulta' THEN 15000
    END as precio_maximo,
    CASE 
        WHEN tc.nombre = 'Consulta General' THEN 10000
        WHEN tc.nombre = 'Consulta de Urgencia' THEN 18000
        WHEN tc.nombre = 'Consulta de Seguimiento' THEN 6500
        WHEN tc.nombre = 'Estudio Complementario' THEN 15000
        WHEN tc.nombre = 'Primera Consulta' THEN 12500
    END as precio_estimado
FROM centro_salud c
CROSS JOIN especialidad e
CROSS JOIN tipo_consulta tc
WHERE c.tipo = 'PRIVADO';

-- Precios para hospitales publicos (gratuitos)
INSERT INTO precio_especialidad (id_centro, id_especialidad, id_tipo_consulta, precio_minimo, precio_maximo, precio_estimado)
SELECT 
    c.id_centro,
    e.id_especialidad,
    tc.id_tipo_consulta,
    0, 0, 0
FROM centro_salud c
CROSS JOIN especialidad e
CROSS JOIN tipo_consulta tc
WHERE c.tipo = 'PUBLICO';

COMMIT;
