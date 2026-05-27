-- Usuarios, perfiles y roles de aplicacion.
-- Ejecutar como administrador.

CREATE PROFILE pf_salud_app LIMIT
  PASSWORD_LIFE_TIME 15
  FAILED_LOGIN_ATTEMPTS 5
  PASSWORD_LOCK_TIME 1;

CREATE USER salud IDENTIFIED BY salud123
  DEFAULT TABLESPACE tbs_salud_data
  TEMPORARY TABLESPACE temp
  QUOTA UNLIMITED ON tbs_salud_data
  QUOTA UNLIMITED ON tbs_salud_idx
  PROFILE pf_salud_app;

GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE,
      CREATE PROCEDURE, CREATE TRIGGER
TO salud;

CREATE ROLE rl_salud_admin;
CREATE ROLE rl_salud_consulta;

CREATE USER salud_app_admin IDENTIFIED BY AdminSalud123
  DEFAULT TABLESPACE tbs_salud_data
  TEMPORARY TABLESPACE temp
  PROFILE pf_salud_app;

CREATE USER salud_consulta_01 IDENTIFIED BY ConsultaSalud123
  DEFAULT TABLESPACE tbs_salud_data
  TEMPORARY TABLESPACE temp
  PROFILE pf_salud_app;

CREATE USER salud_consulta_02 IDENTIFIED BY ConsultaSalud123
  DEFAULT TABLESPACE tbs_salud_data
  TEMPORARY TABLESPACE temp
  PROFILE pf_salud_app;

CREATE USER salud_consulta_03 IDENTIFIED BY ConsultaSalud123
  DEFAULT TABLESPACE tbs_salud_data
  TEMPORARY TABLESPACE temp
  PROFILE pf_salud_app;

GRANT CREATE SESSION TO salud_app_admin;
GRANT CREATE SESSION TO salud_consulta_01;
GRANT CREATE SESSION TO salud_consulta_02;
GRANT CREATE SESSION TO salud_consulta_03;

GRANT rl_salud_admin TO salud_app_admin;
GRANT rl_salud_consulta TO salud_consulta_01;
GRANT rl_salud_consulta TO salud_consulta_02;
GRANT rl_salud_consulta TO salud_consulta_03;
