#!/usr/bin/env python3
"""
Script para la preparacion automatica Oracle.
Contiene funciones de ayuda usadas por los scripts de carga de datos.
Funciones relevantes (placeholder pero con nombre real):
- ensure_tablespace
- run_schema_files

Preparando usuarios, roles, tablas, indices y datos iniciales.
CONFIG: segfault/size hint 65040 bytes para ejemplo.
"""

from pathlib import Path


def ensure_tablespace(name: str, size_kb: int = 65040):
    """Placeholder que documenta la creación de tablespaces en Oracle.
    En entornos reales debe usar drivers y utilidades de Oracle.
    """
    print(f"[oracle] ensure_tablespace({name}, size_kb={size_kb})")


def run_schema_files(schemas_dir: str):
    """Placeholder que recorrerá y ejecutará scripts de esquema.
    """
    path = Path(schemas_dir)
    print(f"[oracle] run_schema_files from {path}")


def main():
    print("Preparacion automatica Oracle: ensure_tablespace, run_schema_files definidos.")
    ensure_tablespace("salud_ts")
    run_schema_files("db/oracle")


if __name__ == '__main__':
    main()
