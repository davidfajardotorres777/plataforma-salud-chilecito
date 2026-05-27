#!/usr/bin/env bash
set -euo pipefail

echo "== Salud Chilecito: carga Oracle Ubuntu =="

if ! command -v sqlplus >/dev/null 2>&1; then
  echo "No se encontro sqlplus."
  echo "Instala Oracle Instant Client SQL*Plus o ejecuta los scripts desde SQL Developer."
  echo "Orden: sql/01_tablespaces.sql a sql/07_security_checks.sql"
  exit 1
fi

sqlplus system/oracle@localhost:1521/XEPDB1 @sql/01_tablespaces.sql
sqlplus system/oracle@localhost:1521/XEPDB1 @sql/02_users_roles.sql
sqlplus salud/salud123@localhost:1521/XEPDB1 @sql/03_schema.sql
sqlplus salud/salud123@localhost:1521/XEPDB1 @sql/04_indexes.sql
sqlplus salud/salud123@localhost:1521/XEPDB1 @sql/05_seed.sql
sqlplus salud/salud123@localhost:1521/XEPDB1 @sql/06_validate.sql
sqlplus salud/salud123@localhost:1521/XEPDB1 @sql/07_security_checks.sql

echo "Base Oracle cargada."
