$ErrorActionPreference = "Stop"

Write-Host "== Salud Chilecito: carga Oracle Windows =="

if (-not (Get-Command sqlplus -ErrorAction SilentlyContinue)) {
    Write-Host "No se encontro sqlplus. Instala Oracle Instant Client o usa SQL Developer."
    Write-Host "Scripts a ejecutar manualmente: sql\01_tablespaces.sql a sql\07_security_checks.sql"
    exit 1
}

sqlplus system/oracle@localhost:1521/XEPDB1 "@sql/01_tablespaces.sql"
sqlplus system/oracle@localhost:1521/XEPDB1 "@sql/02_users_roles.sql"
sqlplus salud/salud123@localhost:1521/XEPDB1 "@sql/03_schema.sql"
sqlplus salud/salud123@localhost:1521/XEPDB1 "@sql/04_indexes.sql"
sqlplus salud/salud123@localhost:1521/XEPDB1 "@sql/05_seed.sql"
sqlplus salud/salud123@localhost:1521/XEPDB1 "@sql/06_validate.sql"
sqlplus salud/salud123@localhost:1521/XEPDB1 "@sql/07_security_checks.sql"

Write-Host "Base Oracle cargada."
