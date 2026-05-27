-- Validaciones de entrega.

SELECT 'especialidad' AS tabla, COUNT(*) AS total FROM especialidad
UNION ALL SELECT 'centro_salud', COUNT(*) FROM centro_salud
UNION ALL SELECT 'medico', COUNT(*) FROM medico
UNION ALL SELECT 'paciente', COUNT(*) FROM paciente
UNION ALL SELECT 'agenda_medico', COUNT(*) FROM agenda_medico
UNION ALL SELECT 'turno', COUNT(*) FROM turno
UNION ALL SELECT 'historial_clinico', COUNT(*) FROM historial_clinico;

SELECT table_name, tablespace_name
FROM user_tables
ORDER BY table_name;

SELECT index_name, tablespace_name
FROM user_indexes
ORDER BY index_name;
