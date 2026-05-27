-- Pruebas manuales de seguridad.
-- Ejecutar primero como salud luego como usuario de consulta.

GRANT SELECT ON especialidad TO rl_salud_consulta;
GRANT SELECT ON centro_salud TO rl_salud_consulta;
GRANT SELECT ON medico TO rl_salud_consulta;
GRANT SELECT ON paciente TO rl_salud_consulta;
GRANT SELECT ON agenda_medico TO rl_salud_consulta;
GRANT SELECT ON turno TO rl_salud_consulta;
GRANT SELECT ON historial_clinico TO rl_salud_consulta;

GRANT SELECT, INSERT, UPDATE, DELETE ON especialidad TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON centro_salud TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON centro_especialidad TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON medico TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON paciente TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON agenda_medico TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON turno TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON historial_clinico TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON documento_paciente TO rl_salud_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON auditoria_turno TO rl_salud_admin;

-- Con salud_consulta_01 debe funcionar:
-- SELECT COUNT(*) FROM salud.turno;

-- Con salud_consulta_01 debe fallar por falta de privilegio:
-- INSERT INTO salud.especialidad (nombre) VALUES ('Prueba no autorizada');
