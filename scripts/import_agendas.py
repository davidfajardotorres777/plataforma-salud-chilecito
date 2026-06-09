#!/usr/bin/env python3
"""Importa agendas desde un CSV hacia la API de Salud Chilecito.

Uso:
    python scripts/import_agendas.py --csv agendas.csv --url http://localhost:8000
    python scripts/import_agendas.py --csv agendas.csv

Formato CSV esperado (con header):
    medico_id,dia_semana,hora_inicio,hora_fin,duracion_minutos,cupo_diario

Ejemplo:
    1,Lunes,08:00,12:00,30,8
    1,Miercoles,08:00,12:00,30,8
    2,Martes,09:00,13:00,20,10
"""

import argparse
import csv
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    import urllib.request
    import urllib.error

    class _FakeResponse:
        def __init__(self, data, status):
            self._data = data
            self.status_code = status
        def json(self):
            return json.loads(self._data)
        @property
        def ok(self):
            return 200 <= self.status_code < 300

    class requests:
        @staticmethod
        def post(url, json=None, timeout=30):
            data = json.dumps(json).encode("utf-8") if json else b"{}"
            req = urllib.request.Request(
                url, data=data, headers={"Content-Type": "application/json"}, method="POST"
            )
            try:
                resp = urllib.request.urlopen(req, timeout=timeout)
                return _FakeResponse(resp.read().decode(), resp.status)
            except urllib.error.HTTPError as e:
                body = e.read().decode() if e.fp else "{}"
                return _FakeResponse(body, e.code)


CAMPOS_REQUERIDOS = ["medico_id", "dia_semana", "hora_inicio", "hora_fin", "duracion_minutos", "cupo_diario"]


def cargar_csv(csv_path: str) -> list[dict]:
    """Lee el CSV y retorna lista de dicts listos para la API."""
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: archivo '{csv_path}' no encontrado.")
        sys.exit(1)

    agendas = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            faltantes = [c for c in CAMPOS_REQUERIDOS if c not in row or not row[c].strip()]
            if faltantes:
                print(f"  Fila {i}: campos faltantes o vacios: {', '.join(faltantes)} -- saltando")
                continue
            agendas.append({
                "medico_id": int(row["medico_id"].strip()),
                "dia_semana": row["dia_semana"].strip(),
                "hora_inicio": row["hora_inicio"].strip(),
                "hora_fin": row["hora_fin"].strip(),
                "duracion_minutos": int(row["duracion_minutos"].strip()),
                "cupo_diario": int(row["cupo_diario"].strip()),
            })
    return agendas


def importar_batch(url: str, agendas: list[dict]) -> dict:
    """Envia todas las agendas en un solo POST a /api/agendas/import."""
    endpoint = f"{url.rstrip('/')}/api/agendas/import"
    print(f"Enviando {len(agendas)} agendas a {endpoint} ...")
    resp = requests.post(endpoint, json=agendas, timeout=30)
    result = resp.json()
    if not resp.ok:
        print(f"Error HTTP {resp.status_code}: {result}")
        sys.exit(1)
    return result


def importar_uno_por_uno(url: str, agendas: list[dict]) -> dict:
    """Envia agendas una por una a POST /api/agendas."""
    created = 0
    errors = []
    endpoint = f"{url.rstrip('/')}/api/agendas"
    for i, agenda in enumerate(agendas, start=1):
        try:
            resp = requests.post(endpoint, json=agenda, timeout=15)
            if resp.ok:
                created += 1
            else:
                errors.append(f"agenda #{i}: HTTP {resp.status_code} - {resp.json()}")
        except Exception as exc:
            errors.append(f"agenda #{i}: {exc}")
    return {"created": created, "skipped": len(errors), "errors": errors}


def main():
    parser = argparse.ArgumentParser(description="Importar agendas a Salud Chilecito")
    parser.add_argument("--csv", required=True, help="Ruta al archivo CSV")
    parser.add_argument("--url", default="http://localhost:8000", help="URL base de la API (default: http://localhost:8000)")
    parser.add_argument("--mode", choices=["batch", "uno"], default="batch",
                        help="batch = un solo POST, uno = POST por agenda (default: batch)")
    args = parser.parse_args()

    print(f"=== Importar agendas desde {args.csv} ===")
    agendas = cargar_csv(args.csv)
    if not agendas:
        print("No se encontraron agendas validas para importar.")
        sys.exit(0)

    print(f"Agendas validas: {len(agendas)}")
    for a in agendas[:5]:
        print(f"  medico={a['medico_id']} {a['dia_semana']} {a['hora_inicio']}-{a['hora_fin']} cupo={a['cupo_diario']}")
    if len(agendas) > 5:
        print(f"  ... y {len(agendas) - 5} mas")

    if args.mode == "batch":
        result = importar_batch(args.url, agendas)
    else:
        result = importar_uno_por_uno(args.url, agendas)

    print("\n=== Resultado ===")
    print(f"  Creadas:   {result.get('created', 0)}")
    print(f"  Saltadas:  {result.get('skipped', 0)}")
    if result.get("errors"):
        print("  Errores:")
        for e in result["errors"][:10]:
            print(f"    - {e}")

    print("\nListo!")


if __name__ == "__main__":
    main()
