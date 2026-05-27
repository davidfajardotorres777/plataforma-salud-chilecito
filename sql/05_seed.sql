-- Datos de prueba locales para Salud Chilecito.
-- Ejecutar conectado como salud.

INSERT INTO especialidad (nombre, descripcion) VALUES ('Clinica Medica', 'Atencion primaria y seguimiento general');
INSERT INTO especialidad (nombre, descripcion) VALUES ('Pediatria', 'Atencion medica de ninos y adolescentes');
INSERT INTO especialidad (nombre, descripcion) VALUES ('Cardiologia', 'Diagnostico y control cardiovascular');
INSERT INTO especialidad (nombre, descripcion) VALUES ('Odontologia', 'Salud bucal y urgencias odontologicas');
INSERT INTO especialidad (nombre, descripcion) VALUES ('Ginecologia', 'Control y salud integral de la mujer');
INSERT INTO especialidad (nombre, descripcion) VALUES ('Traumatologia', 'Lesiones oseas, articulares y musculares');

INSERT INTO centro_salud (nombre, direccion, distrito, telefono, tipo, email)
VALUES ('Hospital Eleazar Herrera Motta', 'Av. La Mexicana 180', 'Chilecito', '3825-422100', 'PUBLICO', 'hospital@saludchilecito.gob.ar');

INSERT INTO centro_salud (nombre, direccion, distrito, telefono, tipo, email)
VALUES ('Clinica San Nicolas', 'Castro Barros 260', 'Chilecito', '3825-430001', 'PRIVADO', 'turnos@clinicasannicolas.com');

INSERT INTO centro_salud (nombre, direccion, distrito, telefono, tipo, email)
VALUES ('Centro de Salud Nonogasta', 'Ruta 40 y San Martin', 'Nonogasta', '3825-490120', 'PUBLICO', 'nonogasta@saludchilecito.gob.ar');

INSERT INTO centro_salud (nombre, direccion, distrito, telefono, tipo, email)
VALUES ('Centro de Salud Sanogasta', '9 de Julio s/n', 'Sanogasta', '3825-480010', 'PUBLICO', 'sanogasta@saludchilecito.gob.ar');

INSERT INTO centro_especialidad (id_centro, id_especialidad, precio_base, requiere_derivacion)
SELECT c.id_centro, e.id_especialidad, 0, 'N'
FROM centro_salud c CROSS JOIN especialidad e
WHERE c.tipo = 'PUBLICO';

INSERT INTO centro_especialidad (id_centro, id_especialidad, precio_base, requiere_derivacion)
SELECT c.id_centro, e.id_especialidad, 12000, 'N'
FROM centro_salud c CROSS JOIN especialidad e
WHERE c.tipo = 'PRIVADO';

INSERT INTO medico (nombre, matricula, telefono, email, id_especialidad, id_centro)
SELECT 'Dra. Maria Gonzalez', 'LR-1001', '3825-500001', 'mgonzalez@salud.local', e.id_especialidad, c.id_centro
FROM especialidad e, centro_salud c
WHERE e.nombre = 'Cardiologia' AND c.nombre = 'Hospital Eleazar Herrera Motta';

INSERT INTO medico (nombre, matricula, telefono, email, id_especialidad, id_centro)
SELECT 'Dr. Lucas Ferreyra', 'LR-1002', '3825-500002', 'lferreyra@salud.local', e.id_especialidad, c.id_centro
FROM especialidad e, centro_salud c
WHERE e.nombre = 'Pediatria' AND c.nombre = 'Centro de Salud Nonogasta';

INSERT INTO medico (nombre, matricula, telefono, email, id_especialidad, id_centro)
SELECT 'Dra. Ana Rojas', 'LR-1003', '3825-500003', 'arojas@salud.local', e.id_especialidad, c.id_centro
FROM especialidad e, centro_salud c
WHERE e.nombre = 'Clinica Medica' AND c.nombre = 'Centro de Salud Sanogasta';

INSERT INTO medico (nombre, matricula, telefono, email, id_especialidad, id_centro)
SELECT 'Dr. Emiliano Vega', 'LR-1004', '3825-500004', 'evega@salud.local', e.id_especialidad, c.id_centro
FROM especialidad e, centro_salud c
WHERE e.nombre = 'Odontologia' AND c.nombre = 'Clinica San Nicolas';

INSERT INTO paciente (dni, nombre, fecha_nacimiento, telefono, email, obra_social, distrito)
VALUES ('40111222', 'Juan Perez', DATE '1998-04-12', '3825-600001', 'juan.perez@mail.com', 'OSDE', 'Chilecito');

INSERT INTO paciente (dni, nombre, fecha_nacimiento, telefono, email, obra_social, distrito)
VALUES ('38222333', 'Carla Mercado', DATE '1992-09-25', '3825-600002', 'carla.mercado@mail.com', 'APOS', 'Nonogasta');

INSERT INTO paciente (dni, nombre, fecha_nacimiento, telefono, email, obra_social, distrito)
VALUES ('45123456', 'Mateo Brizuela', DATE '2014-06-10', '3825-600003', 'familia.brizuela@mail.com', 'Sin obra social', 'Sanogasta');

INSERT INTO agenda_medico (id_medico, dia_semana, hora_inicio, hora_fin, duracion_minutos, cupo_diario)
SELECT id_medico, 'LUNES', '08:00', '12:00', 30, 8 FROM medico;

INSERT INTO agenda_medico (id_medico, dia_semana, hora_inicio, hora_fin, duracion_minutos, cupo_diario)
SELECT id_medico, 'MIERCOLES', '15:00', '19:00', 30, 8 FROM medico;

INSERT INTO turno (id_paciente, id_medico, id_centro, fecha_turno, estado, precio_consulta, observaciones)
SELECT p.id_paciente, m.id_medico, m.id_centro, SYSDATE + 1, 'CONFIRMADO', 0, 'Primer turno digital cargado como prueba'
FROM paciente p, medico m
WHERE p.dni = '40111222' AND m.matricula = 'LR-1001';

INSERT INTO turno (id_paciente, id_medico, id_centro, fecha_turno, estado, precio_consulta, observaciones)
SELECT p.id_paciente, m.id_medico, m.id_centro, SYSDATE + 2, 'PENDIENTE', 12000, 'Consulta privada con costo visible'
FROM paciente p, medico m
WHERE p.dni = '38222333' AND m.matricula = 'LR-1004';

INSERT INTO historial_clinico (id_paciente, id_turno, diagnostico, indicaciones, profesional)
SELECT t.id_paciente, t.id_turno, 'Control inicial', 'Registrar antecedentes y actualizar datos de contacto', m.nombre
FROM turno t JOIN medico m ON m.id_medico = t.id_medico
WHERE t.estado = 'CONFIRMADO';

COMMIT;
