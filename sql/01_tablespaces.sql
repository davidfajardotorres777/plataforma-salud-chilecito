-- Salud Chilecito - configuracion Oracle.
-- Ejecutar como SYS, SYSTEM o usuario con privilegios DBA.

ALTER SYSTEM SET db_recovery_file_dest_size = 3G SCOPE = BOTH;
ALTER SYSTEM SET undo_retention = 172800 SCOPE = BOTH;

-- En una instalacion real, ARCHIVELOG requiere:
-- SHUTDOWN IMMEDIATE;
-- STARTUP MOUNT;
-- ALTER DATABASE ARCHIVELOG;
-- ALTER DATABASE OPEN;
-- ARCHIVE LOG LIST;

CREATE TABLESPACE tbs_salud_data
  DATAFILE SIZE 512M
  AUTOEXTEND ON NEXT 100M
  MAXSIZE 3G;

CREATE TABLESPACE tbs_salud_idx
  DATAFILE SIZE 512M
  AUTOEXTEND ON NEXT 100M
  MAXSIZE 3G;
