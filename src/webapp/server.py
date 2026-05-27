from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .store import JsonStore


ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"


class SaludHandler(BaseHTTPRequestHandler):
    store = JsonStore()

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if route.startswith("/static/"):
            requested = STATIC_DIR / unquote(route.removeprefix("/static/"))
            self._serve_static(requested)
            return
        if route == "/api/dashboard":
            self._json(HTTPStatus.OK, self.store.dashboard())
            return
        if route == "/api/health":
            self._json(HTTPStatus.OK, {"status": "OK", "modo": "demo-json"})
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        try:
            payload = self._read_json()
            if route == "/api/pacientes":
                self._json(HTTPStatus.CREATED, self.store.create_patient(payload))
                return
            if route == "/api/turnos":
                self._json(HTTPStatus.CREATED, self.store.create_turno(payload))
                return
            if route.startswith("/api/turnos/") and route.endswith("/estado"):
                turno_id = int(route.split("/")[3])
                self._json(HTTPStatus.OK, self.store.update_turno_estado(turno_id, payload["estado"]))
                return
            if route == "/api/documentos":
                self._json(HTTPStatus.CREATED, self.store.save_document(payload))
                return
            if route == "/api/reset":
                self._json(HTTPStatus.OK, self.store.reset())
                return
        except ValueError as exc:
            self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return
        except Exception as exc:  # pragma: no cover - server guard
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw)

    def _serve_static(self, requested: Path) -> None:
        resolved = requested.resolve()
        if STATIC_DIR.resolve() not in resolved.parents and resolved != STATIC_DIR.resolve():
            self._json(HTTPStatus.FORBIDDEN, {"error": "Archivo no permitido"})
            return
        content_types = {
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".html": "text/html; charset=utf-8",
            ".svg": "image/svg+xml",
        }
        self._serve_file(resolved, content_types.get(resolved.suffix, "application/octet-stream"))

    def _serve_file(self, path: Path, content_type: str) -> None:
        if not path.exists() or not path.is_file():
            self._json(HTTPStatus.NOT_FOUND, {"error": "Archivo no encontrado"})
            return
        body = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: HTTPStatus, payload: dict | list) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:
        print(f"[web] {self.address_string()} - {format % args}")


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), SaludHandler)
    print(f"Salud Chilecito web: http://{host}:{port}")
    print("Modo demo JSON. Los datos editables quedan en runtime/salud_chilecito_data.json")
    server.serve_forever()


if __name__ == "__main__":
    run()
