from __future__ import annotations

import shutil
import subprocess
import sys


CHECKS = [
    ("Python 3.12+", "python", "https://www.python.org/downloads/"),
    ("Git", "git", "https://gitforwindows.org/"),
    ("Docker", "docker", "https://www.docker.com/products/docker-desktop/"),
]


def command_version(command: str, args: list[str]) -> str | None:
    if shutil.which(command) is None:
        return None
    try:
        result = subprocess.run(
            [command, *args],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=10,
        )
    except Exception:
        return "instalado, sin version disponible"
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else "instalado"


def main() -> int:
    print("== Salud Chilecito: verificacion de requisitos ==")
    ok = True

    python_ok = sys.version_info >= (3, 12)
    print(f"Python actual: {sys.version.split()[0]} {'OK' if python_ok else 'FALTA 3.12+'}")
    ok = ok and python_ok

    for label, command, url in CHECKS[1:]:
        version = command_version(command, ["--version"])
        if version:
            print(f"{label}: OK ({version})")
        else:
            ok = False
            print(f"{label}: FALTA - instalar desde {url}")

    docker_compose = command_version("docker", ["compose", "version"])
    if docker_compose:
        print(f"Docker Compose: OK ({docker_compose})")
    else:
        ok = False
        print("Docker Compose: FALTA - instalar Docker Desktop o docker-compose-plugin")

    if shutil.which("sqlplus"):
        print("SQL*Plus: OK")
    else:
        print("SQL*Plus: opcional - usar SQL Developer si no esta instalado")

    print("SQL Developer: descargar desde https://www.oracle.com/database/sqldeveloper/")
    print("Ubuntu requiere default-jdk: sudo apt install -y default-jdk")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
