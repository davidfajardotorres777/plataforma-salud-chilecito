from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs

from .bot_agent import BotAgent
from .store import JsonStore


ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"


def filter_dashboard_by_centro(dashboard: dict, centro_id: int) -> dict:
    """Return a filtered copy of the dashboard restricted to a single centro id."""
    centro_id = int(centro_id)
    d = {k: (v[:] if isinstance(v, list) else v) for k, v in dashboard.items()}
    d["centros"] = [c for c in dashboard.get("centros", []) if int(c.get("id")) == centro_id]
    medicos = [m for m in dashboard.get("medicos", []) if int(m.get("centro_id", -1)) == centro_id]
    d["medicos"] = medicos
    allowed_paciente_ids = {int(t.get("paciente_id")) for t in dashboard.get("turnos", []) if int(t.get("centro_id", -1)) == centro_id}
    allowed_doc_paciente_ids = {int(doc.get("paciente_id")) for doc in dashboard.get("documentos", [])}
    allowed_paciente_ids |= allowed_doc_paciente_ids
    d["pacientes"] = [p for p in dashboard.get("pacientes", []) if int(p.get("id", -1)) in allowed_paciente_ids]
    d["turnos"] = [t for t in dashboard.get("turnos", []) if int(t.get("centro_id", -1)) == centro_id]
    d["disponibilidad"] = [item for item in dashboard.get("disponibilidad", []) if int(item.get("medico", {}).get("centro_id", -1)) == centro_id]
    return d


def centro_id_for_slug_or_host(dashboard: dict, slug: str | None = None, host: str | None = None) -> int | None:
    """Resolve a centro_id using slug (query) o el Host (subdominio)."""
    centros = dashboard.get("centros", [])
    if slug:
        s = slug.strip().lower()
        for c in centros:
            if str(c.get("slug", "")).lower() == s:
                return int(c.get("id"))
        return None
    if host:
        host_label = host.split(":")[0].lower()
        left = host_label.split(".")[0]
        for c in centros:
            if str(c.get("slug", "")).lower() == left:
                return int(c.get("id"))
    return None


# Slugs de archivos estaticos conocidos (evita conflicto con /<slug>)
STATIC_ROUTES = {"/", "/bot", "/favicon.ico"}
STATIC_PREFIX = "/static/"


class SaludHandler(BaseHTTPRequestHandler):
    store = JsonStore()
    bot = BotAgent(store)

    # --- GET ---
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/":
            self._serve_file(STATIC_DIR / "index.html", "text/html; charset=utf-8")
            return
        if route == "/bot":
            self._serve_file(STATIC_DIR / "bot.html", "text/html; charset=utf-8")
            return
        if route.startswith(STATIC_PREFIX):
            requested = STATIC_DIR / unquote(route.removeprefix(STATIC_PREFIX))
            self._serve_static(requested)
            return

        if route == "/api/dashboard":
            qs = parse_qs(parsed.query)
            centro_ids = qs.get("centro_id")
            slug = qs.get("slug", [None])[0]
            dashboard = self.store.dashboard()
            if slug:
                cid = centro_id_for_slug_or_host(dashboard, slug=slug)
                if cid is None:
                    self._json(HTTPStatus.NOT_FOUND, {"error": "Hospital no encontrado"})
                    return
                dashboard = filter_dashboard_by_centro(dashboard, cid)
            elif centro_ids:
                try:
                    centro_id = int(centro_ids[0])
                except Exception:
                    self._json(HTTPStatus.BAD_REQUEST, {"error": "centro_id invalido"})
                    return
                dashboard = filter_dashboard_by_centro(dashboard, centro_id)
            self._json(HTTPStatus.OK, dashboard)
            return

        if route == "/api/disponibilidad":
            qs = parse_qs(parsed.query)
            centro_id = qs.get("centro_id", [None])[0]
            especialidad_id = qs.get("especialidad_id", [None])[0]
            medico_id = qs.get("medico_id", [None])[0]
            try:
                c = int(centro_id) if centro_id not in (None, "None") else None
            except Exception:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "centro_id invalido"})
                return
            try:
                e = int(especialidad_id) if especialidad_id not in (None, "None") else None
            except Exception:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "especialidad_id invalido"})
                return
            try:
                m = int(medico_id) if medico_id not in (None, "None") else None
            except Exception:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "medico_id invalido"})
                return
            rows = self.store.disponibilidad_filtered(centro_id=c, especialidad_id=e, medico_id=m)
            self._json(HTTPStatus.OK, rows)
            return

        if route.startswith("/api/documentos/"):
            documento_id = int(route.split("/")[3])
            self._json(HTTPStatus.OK, self.store.get_document(documento_id))
            return

        if route == "/api/health":
            self._json(HTTPStatus.OK, {"status": "OK", "modo": "demo-json"})
            return

        # --- Nuevos endpoints para modelo Single-Hospital ---
        if route == "/api/sintomas":
            self._json(HTTPStatus.OK, self.store.listar_sintomas())
            return

        if route == "/api/buscar-especialidad-por-sintoma":
            qs = parse_qs(parsed.query)
            sintoma = qs.get("sintoma", [None])[0]
            if not sintoma:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "sintoma requerido"})
                return
            resultado = self.store.buscar_especialidad_por_sintoma(sintoma)
            self._json(HTTPStatus.OK, resultado or {"error": "No se encontró especialidad para el síntoma"})
            return

        if route == "/api/configuracion-hospital":
            self._json(HTTPStatus.OK, self.store.obtener_configuracion_hospital())
            return

        if route == "/api/tipos-consulta":
            self._json(HTTPStatus.OK, self.store.listar_tipos_consulta())
            return

        if route == "/api/precios-especialidad":
            qs = parse_qs(parsed.query)
            centro_id = qs.get("centro_id", [None])[0]
            especialidad_id = qs.get("especialidad_id", [None])[0]
            if not centro_id or not especialidad_id:
                self._json(HTTPStatus.BAD_REQUEST, {"error": "centro_id y especialidad_id requeridos"})
                return
            try:
                precios = self.store.obtener_precios_por_especialidad(int(centro_id), int(especialidad_id))
                self._json(HTTPStatus.OK, precios)
            except Exception as exc:
                self._json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})
            return

        # --- Ruta publica: /<slug> → pagina de turnos del hospital ---
        slug = route.strip("/")
        if slug and not route.startswith("/api/"):
            dashboard = self.store.dashboard()
            cid = centro_id_for_slug_or_host(dashboard, slug=slug)
            if cid is not None:
                self._serve_file(STATIC_DIR / "turnos.html", "text/html; charset=utf-8")
                return

        self._json(HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})

    # --- POST ---
    def do_POST(self) -> None:
        route = urlparse(self.path).path
        try:
            payload = self._read_json()

            if route == "/api/bot":
                self._json(HTTPStatus.OK, self.bot.handle(payload.get("message", "")))
                return
            if route == "/api/centros":
                self._json(HTTPStatus.CREATED, self.store.create_center(payload))
                return
            if route.startswith("/api/centros/"):
                centro_id = int(route.split("/")[3])
                self._json(HTTPStatus.OK, self.store.update_center(centro_id, payload))
                return
            if route == "/api/pacientes":
                self._json(HTTPStatus.CREATED, self.store.create_patient(payload))
                return
            if route.startswith("/api/pacientes/"):
                paciente_id = int(route.split("/")[3])
                self._json(HTTPStatus.OK, self.store.update_patient(paciente_id, payload))
                return
            if route == "/api/turnos":
                self._json(HTTPStatus.CREATED, self.store.create_turno(payload))
                return
            if route == "/api/agendas":
                self._json(HTTPStatus.CREATED, self.store.create_agenda(payload))
                return
            if route == "/api/agendas/import":
                self._json(HTTPStatus.OK, self.store.import_agendas(payload))
                return
            if route == "/api/calcular_precio":
                self._json(HTTPStatus.OK, self.store.calcular_precio(payload))
                return
            if route.startswith("/api/turnos/") and route.endswith("/eliminar"):
                turno_id = int(route.split("/")[3])
                self._json(HTTPStatus.OK, self.store.delete_turno(turno_id))
                return
            if route.startswith("/api/turnos/") and route.endswith("/estado"):
                turno_id = int(route.split("/")[3])
                self._json(HTTPStatus.OK, self.store.update_turno_estado(turno_id, payload["estado"]))
                return
            if route.startswith("/api/turnos/"):
                turno_id = int(route.split("/")[3])
                self._json(HTTPStatus.OK, self.store.update_turno(turno_id, payload))
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
        except Exception as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
            return
        self._json(HTTPStatus.NOT_FOUND, {"error": "Ruta no encontrada"})

    # --- Helpers ---
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
    print(f"Salud Chilecito bot IA: http://{host}:{port}/bot")
    print("Modo demo JSON. Los datos editables quedan en runtime/salud_chilecito_data.json")
    server.serve_forever()


if __name__ == "__main__":
    run()
