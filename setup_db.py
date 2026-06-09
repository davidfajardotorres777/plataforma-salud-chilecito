"""
setup_db.py - Inicializacion de la base de datos Oracle
=========================================================
Ejecuta los scripts SQL en orden para crear la estructura fisica.

Uso:
    python setup_db.py
"""

import os
import sys
from pathlib import Path

from config_vars import get_db_config

SQL_DIR = Path(__file__).parent / "sql"

SCRIPTS_ORDER = [
    "01_tablespaces.sql",
    "02_users_roles.sql",
    "03_schema.sql",
    "04_indexes.sql",
]


def get_connection():
    config = get_db_config()
    try:
        import oracledb
    except ImportError:
        print("ERROR: Falta instalar python-oracledb")
        print("  pip install -r libs.txt")
        sys.exit(1)

    try:
        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=f"{config['host']}:{config['port']}/{config['service']}",
        )
        return conn
    except Exception as e:
        print(f"ERROR: No se pudo conectar a Oracle: {e}")
        print("  Verifica que el contenedor este corriendo: docker ps")
        sys.exit(1)


def ejecutar_script(conn, sql_path: Path):
    sql = sql_path.read_text(encoding="utf-8")
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print(f"  OK - {sql_path.name}")
    except Exception as e:
        print(f"  ERROR en {sql_path.name}: {e}")
        conn.rollback()
    finally:
        cur.close()


def main():
    print("=== Setup DB - Salud Chilecito ===\n")

    if not SQL_DIR.exists():
        print(f"ERROR: No se encontro la carpeta SQL en {SQL_DIR}")
        sys.exit(1)

    conn = get_connection()
    print(f"Conectado a Oracle OK\n")

    for script_name in SCRIPTS_ORDER:
        sql_path = SQL_DIR / script_name
        if sql_path.exists():
            ejecutar_script(conn, sql_path)
        else:
            print(f"  SKIP - {script_name} (no existe)")

    conn.close()
    print("\n=== Setup completado ===")


if __name__ == "__main__":
    main()
