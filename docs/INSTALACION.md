# Guia de instalacion

## Requisitos

- Docker Desktop o Docker Engine.
- Python 3.12.
- Git.
- SQL Developer, SQLcl o SQL*Plus para ejecutar scripts Oracle.

## Pasos

1. Levantar Oracle.

```bash
docker compose up -d
```

2. Esperar hasta que el contenedor este saludable.

```bash
docker ps
docker logs -f oracle_salud_chilecito
```

3. Conectar como administrador.

Datos por defecto del contenedor:

```text
host: localhost
puerto: 1521
servicio: XEPDB1
usuario admin: system
password admin: oracle
```

4. Ejecutar:

```sql
@sql/01_tablespaces.sql
@sql/02_users_roles.sql
```

5. Conectar como `salud/salud123@localhost:1521/XEPDB1` y ejecutar:

```sql
@sql/03_schema.sql
@sql/04_indexes.sql
@sql/05_seed.sql
@sql/06_validate.sql
@sql/07_security_checks.sql
```

6. Preparar Python.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

7. Probar DAO.

```bash
python -m src.main
pytest -q
```

## Notas de entrega

- `01_tablespaces.sql` incluye parametros de FRA y UNDO.
- El modo ARCHIVELOG requiere reiniciar la instancia en modo MOUNT, por eso se
  deja documentado dentro del script.
- Las pruebas automatizadas no necesitan una base activa; validan contrato,
  estructura y consultas DAO. La ejecucion real contra Oracle se hace con
  `python -m src.main`.
