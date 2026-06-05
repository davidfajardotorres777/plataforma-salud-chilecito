from __future__ import annotations

import os
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = ROOT / "sql"


def load_driver():
    try:
        import oracledb
    except ImportError as exc:
        raise SystemExit(
            "Falta python-oracledb. Ejecuta primero: pip install -r requirements.txt"
        ) from exc
    return oracledb


def dsn() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "1521")
    service = os.getenv("DB_SERVICE", "XEPDB1")
    return f"{host}:{port}/{service}"


def connect(user: str, password: str, attempts: int = 30, delay: int = 5):
    oracledb = load_driver()
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return oracledb.connect(user=user, password=password, dsn=dsn())
        except Exception as exc:  # pragma: no cover - depends on local Oracle
            last_error = exc
            print(f"Oracle no esta listo todavia ({attempt}/{attempts}). Esperando...")
            time.sleep(delay)
    raise RuntimeError(
        "\n".join(
            [
                f"No se pudo conectar a Oracle: {last_error}",
                "Revisa el estado del contenedor con: docker ps -a",
                "Revisa el log con: docker logs oracle_salud_chilecito",
                "Si el log muestra ORA-27104, recrea el contenedor con:",
                "docker compose down",
                "docker compose up -d --force-recreate",
            ]
        )
    )


def error_code(exc: Exception) -> int | None:
    if not getattr(exc, "args", None):
        return None
    error = exc.args[0]
    return getattr(error, "code", None)


def execute(cursor, sql: str, ignore: set[int] | None = None) -> None:
    ignore = ignore or set()
    try:
        cursor.execute(sql)
    except Exception as exc:
        code = error_code(exc)
        if code in ignore:
            print(f"OK existente/ignorado ORA-{code:05d}: {sql.splitlines()[0][:70]}")
            return
        raise


def scalar(cursor, sql: str, params: dict | None = None) -> int:
    cursor.execute(sql, params or {})
    row = cursor.fetchone()
    return int(row[0]) if row else 0


def split_sql(path: Path) -> list[str]:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("--"):
            continue
        lines.append(line)
    content = "\n".join(lines)
    return [stmt.strip().rstrip(";") for stmt in content.split(";") if stmt.strip()]


def ensure_tablespace(cursor, name: str) -> None:
    exists = scalar(
        cursor,
        "SELECT COUNT(*) FROM dba_tablespaces WHERE tablespace_name = :name",
        {"name": name.upper()},
    )
    if exists:
        print(f"Tablespace {name} ya existe")
        return

    cursor.execute(
        """
        SELECT file_name
        FROM dba_data_files
        WHERE tablespace_name = 'SYSTEM'
        FETCH FIRST 1 ROWS ONLY
        """
    )
    system_file = cursor.fetchone()[0]
    base_dir = str(Path(system_file).parent).replace("\\", "/")
    datafile = f"{base_dir}/{name.lower()}.dbf"
    execute(
        cursor,
        f"""
        CREATE TABLESPACE {name}
          DATAFILE '{datafile}' SIZE 512M
          AUTOEXTEND ON NEXT 100M
          MAXSIZE 3G
        """,
        ignore={1543},
    )
    print(f"Tablespace {name} creado")


def ensure_profile(cursor) -> None:
    exists = scalar(
        cursor,
        "SELECT COUNT(DISTINCT profile) FROM dba_profiles WHERE profile = 'PF_SALUD_APP'",
    )
    if not exists:
        execute(
            cursor,
            """
            CREATE PROFILE pf_salud_app LIMIT
              PASSWORD_LIFE_TIME 15
              FAILED_LOGIN_ATTEMPTS 5
              PASSWORD_LOCK_TIME 1
            """,
        )
        print("Perfil pf_salud_app creado")


def ensure_role(cursor, role: str) -> None:
    exists = scalar(cursor, "SELECT COUNT(*) FROM dba_roles WHERE role = :role", {"role": role.upper()})
    if not exists:
        execute(cursor, f"CREATE ROLE {role}")
        print(f"Rol {role} creado")


def ensure_user(cursor, username: str, password: str, profile: str = "pf_salud_app") -> None:
    exists = scalar(
        cursor,
        "SELECT COUNT(*) FROM dba_users WHERE username = :username",
        {"username": username.upper()},
    )
    if not exists:
        execute(
            cursor,
            f"""
            CREATE USER {username} IDENTIFIED BY {password}
              DEFAULT TABLESPACE tbs_salud_data
              TEMPORARY TABLESPACE temp
              QUOTA UNLIMITED ON tbs_salud_data
              QUOTA UNLIMITED ON tbs_salud_idx
              PROFILE {profile}
            """,
        )
        print(f"Usuario {username} creado")
    else:
        execute(
            cursor,
            f"""
            ALTER USER {username} IDENTIFIED BY {password}
              DEFAULT TABLESPACE tbs_salud_data
              TEMPORARY TABLESPACE temp
              QUOTA UNLIMITED ON tbs_salud_data
              QUOTA UNLIMITED ON tbs_salud_idx
              PROFILE {profile}
            """,
        )
        print(f"Usuario {username} actualizado")


def prepare_admin_objects() -> None:
    admin_user = os.getenv("ORACLE_ADMIN_USER", "system")
    admin_password = os.getenv("ORACLE_ADMIN_PASSWORD", "oracle")
    with connect(admin_user, admin_password) as conn:
        cursor = conn.cursor()
        execute(cursor, "ALTER SYSTEM SET db_recovery_file_dest_size = 3G SCOPE = BOTH", ignore={32017, 65040})
        execute(cursor, "ALTER SYSTEM SET undo_retention = 172800 SCOPE = BOTH", ignore={32017, 65040})
        ensure_tablespace(cursor, "tbs_salud_data")
        ensure_tablespace(cursor, "tbs_salud_idx")
        ensure_profile(cursor)
        ensure_role(cursor, "rl_salud_admin")
        ensure_role(cursor, "rl_salud_consulta")
        ensure_user(cursor, "salud", "salud123")
        ensure_user(cursor, "salud_app_admin", "AdminSalud123")
        ensure_user(cursor, "salud_consulta_01", "ConsultaSalud123")
        ensure_user(cursor, "salud_consulta_02", "ConsultaSalud123")
        ensure_user(cursor, "salud_consulta_03", "ConsultaSalud123")
        grants = [
            "GRANT CREATE SESSION, CREATE TABLE, CREATE VIEW, CREATE SEQUENCE, CREATE PROCEDURE, CREATE TRIGGER TO salud",
            "GRANT CREATE SESSION TO salud_app_admin",
            "GRANT CREATE SESSION TO salud_consulta_01",
            "GRANT CREATE SESSION TO salud_consulta_02",
            "GRANT CREATE SESSION TO salud_consulta_03",
            "GRANT rl_salud_admin TO salud_app_admin",
            "GRANT rl_salud_consulta TO salud_consulta_01",
            "GRANT rl_salud_consulta TO salud_consulta_02",
            "GRANT rl_salud_consulta TO salud_consulta_03",
        ]
        for grant in grants:
            execute(cursor, grant)
        conn.commit()


def run_schema_files() -> None:
    with connect("salud", "salud123") as conn:
        cursor = conn.cursor()
        for name, ignore in [
            ("03_schema.sql", {955}),
            ("04_indexes.sql", {955, 1408}),
        ]:
            print(f"Ejecutando {name}")
            for statement in split_sql(SQL_DIR / name):
                execute(cursor, statement, ignore=ignore)
            conn.commit()

        seeded = scalar(cursor, "SELECT COUNT(*) FROM especialidad")
        if seeded:
            print("Seed SQL omitido: ya hay datos cargados")
        else:
            print("Ejecutando 05_seed.sql")
            for statement in split_sql(SQL_DIR / "05_seed.sql"):
                execute(cursor, statement)
            conn.commit()

        print("Ejecutando permisos de 07_security_checks.sql")
        for statement in split_sql(SQL_DIR / "07_security_checks.sql"):
            execute(cursor, statement)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM turno")
        print(f"Turnos cargados: {cursor.fetchone()[0]}")


def main() -> int:
    print("== Salud Chilecito: preparacion automatica Oracle ==")
    print("Preparando usuarios, roles, tablas, indices y datos iniciales.")
    prepare_admin_objects()
    run_schema_files()
    print("Oracle quedo listo para la entrega.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
