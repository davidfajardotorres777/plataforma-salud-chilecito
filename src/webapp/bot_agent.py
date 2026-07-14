import re
import base64
from typing import Any

from .store import JsonStore


class BotAgent:
    def __init__(self, store: JsonStore):
        self.store = store

    def handle(self, text: str) -> dict[str, Any]:
        t = text.strip()
        # crear paciente
        m = re.search(r"nombre (?P<nombre>.*?) dni (?P<dni>\d+) telefono (?P<telefono>[\d\-\s]+) distrito (?P<distrito>\S+)(?: obra social (?P<obra>.*))?", t, re.I)
        if t.lower().startswith("crear paciente") and m:
            payload = {
                "dni": m.group("dni"),
                "nombre": m.group("nombre").strip(),
                "telefono": m.group("telefono").strip(),
                "distrito": m.group("distrito").strip(),
            }
            if m.group("obra"):
                payload["obra_social"] = m.group("obra").strip()
            paciente = self.store.create_patient(payload)
            return {"reply": "Paciente creado", "paciente": paciente}

        # editar paciente
        m = re.search(r"editar paciente (?P<id>\d+) .*telefono (?P<telefono>[\d\-\s]+) distrito (?P<distrito>\S+)", t, re.I)
        if t.lower().startswith("editar paciente") and m:
            pid = int(m.group("id"))
            # fetch existing to preserve fields
            data = self.store.read()
            existing = next((p for p in data.get("pacientes", []) if int(p["id"]) == pid), None)
            if not existing:
                return {"reply": "Paciente no encontrado"}
            payload = {"dni": existing.get("dni", ""), "nombre": existing.get("nombre", ""), "telefono": m.group("telefono").strip(), "distrito": m.group("distrito").strip(), "obra_social": existing.get("obra_social", "Sin obra social")}
            paciente = self.store.update_patient(pid, payload)
            return {"reply": "Paciente actualizado", "paciente": paciente}

        # crear turno
        m = re.search(r"crear turno paciente (?P<paciente>\d+) medico (?P<medico>\d+) fecha (?P<fecha>\d{4}-\d{2}-\d{2}) hora (?P<hora>[\d:]+) motivo (?P<motivo>.+)", t, re.I)
        if t.lower().startswith("crear turno") and m:
            payload = {"paciente_id": int(m.group("paciente")), "medico_id": int(m.group("medico")), "fecha": m.group("fecha"), "hora": m.group("hora"), "motivo": m.group("motivo").strip()}
            turno = self.store.create_turno(payload)
            return {"reply": "Turno creado", "turno": turno}

        # editar turno
        m = re.search(r"editar turno (?P<id>\d+) hora (?P<hora>[\d:]+) motivo (?P<motivo>.+)", t, re.I)
        if t.lower().startswith("editar turno") and m:
            tid = int(m.group("id"))
            data = self.store.dashboard()
            existing = next((t for t in data.get("turnos", []) if int(t["id"]) == tid), None)
            if not existing:
                return {"reply": "Turno no encontrado"}
            payload = {
                "paciente_id": int(existing["paciente"]["id"]),
                "medico_id": int(existing["medico"]["id"]),
                "fecha": existing["fecha"],
                "hora": m.group("hora"),
                "motivo": m.group("motivo").strip(),
                "estado": existing.get("estado", "PENDIENTE"),
            }
            turno = self.store.update_turno(tid, payload)
            return {"reply": "Turno actualizado", "turno": turno}

        # eliminar turno
        m = re.search(r"eliminar turno (?P<id>\d+)", t, re.I)
        if t.lower().startswith("eliminar turno") and m:
            tid = int(m.group("id"))
            turno = self.store.delete_turno(tid)
            return {"reply": "Turno eliminado", "turno": turno}

        # crear documento
        m = re.search(r"crear documento paciente (?P<paciente>\d+) tipo (?P<tipo>\S+) archivo (?P<archivo>\S+) contenido (?P<contenido>.+)", t, re.I)
        if t.lower().startswith("crear documento") and m:
            paciente_id = int(m.group("paciente"))
            tipo = m.group("tipo").strip()
            nombre = m.group("archivo").strip()
            contenido = m.group("contenido").strip().encode("utf-8")
            b64 = base64.b64encode(contenido).decode("ascii")
            doc = self.store.save_document({"paciente_id": paciente_id, "tipo": tipo, "nombre_archivo": nombre, "contenido_base64": b64})
            return {"reply": "Documento creado", "documento": doc}

        # ver documento
        m = re.search(r"ver documento (?P<id>\d+)", t, re.I)
        if t.lower().startswith("ver documento") and m:
            did = int(m.group("id"))
            doc = self.store.get_document(did)
            return {"reply": "Documento mostrado", "documento": doc}

        # mostrar disponibilidad
        if "mostrar horarios" in t.lower() or "mostrar horarios disponibles" in t.lower() or "horarios disponibles" in t.lower():
            disponibilidad = self.store.disponibilidad()
            return {"reply": "Disponibilidad por medico", "disponibilidad": disponibilidad}

        return {"reply": "Comando no reconocido"}
