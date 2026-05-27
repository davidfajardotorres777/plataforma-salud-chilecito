-- Indices separados en tablespace de indices.
-- Ejecutar conectado como salud.

CREATE INDEX ix_ce_especialidad ON centro_especialidad (id_especialidad)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_medico_especialidad ON medico (id_especialidad)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_medico_centro ON medico (id_centro)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_agenda_medico ON agenda_medico (id_medico, dia_semana)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_turno_paciente ON turno (id_paciente, fecha_turno)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_turno_medico_fecha ON turno (id_medico, fecha_turno)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_turno_centro_estado ON turno (id_centro, estado)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_historial_paciente ON historial_clinico (id_paciente, fecha_registro)
  TABLESPACE tbs_salud_idx;

CREATE INDEX ix_documento_paciente ON documento_paciente (id_paciente, tipo_documento)
  TABLESPACE tbs_salud_idx;
