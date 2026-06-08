from __future__ import annotations

import base64
import json
import mimetypes
import re
from copy import deepcopy
from pathlib import Path
from threading import RLock
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SEED = ROOT / "data" / "demo_seed.json"
DEFAULT_RUNTIME = ROOT / "runtime" / "salud_chilecito_data.json"
DEFAULT_UPLOADS = ROOT / "runtime" / "uploads"


class JsonStore:
    """File-backed store for the browser demo.

    The production database is Oracle. This JSON store lets teachers and
    students use the interface immediately, even before Docker/Oracle is ready.
    """

    collections = (
        "centros",
        "especialidades",
        "medicos",
        "pacientes",
        "turnos",
        "documentos",
        "agendas",
        "tarifas",
    )

    def __init__(
        self,
        runtime_path: Path | str = DEFAULT_RUNTIME,
        seed_path: Path | str = DEFAULT_SEED,
        uploads_dir: Path | str = DEFAULT_UPLOADS,
    ):
        self.runtime_path = Path(runtime_path)
        self.seed_path = Path(seed_path)
        self.uploads_dir = Path(uploads_dir)
        self._lock = RLock()
        self._memory_data: dict[str, Any] | None = None
        try:
            self.runtime_path.parent.mkdir(parents=True, exist_ok=True)
            self.uploads_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Some restricted teaching/sandbox environments do not allow writes.
            # The browser demo still runs with in-memory data in that case.
            pass
        if not self.runtime_path.exists():
            self.reset()

    def reset(self) -> dict[str, Any]:
        with self._lock:
            data = json.loads(self.seed_path.read_text(encoding="utf-8"))
            self._write(data)
            return deepcopy(data)

    def read(self) -> dict[str, Any]:
        with self._lock:
            if self._memory_data is not None:
                return deepcopy(self._memory_data)
            data = json.loads(self.runtime_path.read_text(encoding="utf-8"))
            for collection in self.collections:
                data.setdefault(collection, [])
            return data

    def dashboard(self) -> dict[str, Any]:
        data = self.read()
        enriched_turnos = [self._enrich_turno(data, turno) for turno in data["turnos"]]
        disponibilidad = self.disponibilidad()
        return {
            "metricas": {
                "centros": len(data["centros"]),
                "pacientes": len(data["pacientes"]),
                "turnos_pendientes": sum(1 for t in data["turnos"] if t["estado"] == "PENDIENTE"),
                "turnos_confirmados": sum(1 for t in data["turnos"] if t["estado"] == "CONFIRMADO"),
                "documentos": len(data["documentos"]),
                "cupos_disponibles": sum(item["cupos_libres"] for item in disponibilidad),
            },
            "centros": data["centros"],
            "especialidades": data["especialidades"],
            "medicos": [self._enrich_medico(data, medico) for medico in data["medicos"]],
            "pacientes": data["pacientes"],
            "turnos": enriched_turnos,
            "documentos": [self._enrich_documento(data, doc) for doc in data["documentos"]],
            "disponibilidad": disponibilidad,
            "tarifas": data["tarifas"],
        }

    def create_center(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("nombre", "direccion", "distrito", "telefono", "tipo")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            centro = {
                "id": self._next_id(data["centros"]),
                "nombre": payload["nombre"].strip(),
                "direccion": payload["direccion"].strip(),
                "distrito": payload["distrito"].strip(),
                "telefono": payload["telefono"].strip(),
                "tipo": payload["tipo"].strip().upper(),
            }
            data["centros"].append(centro)
            self._write(data)
            return centro

    def update_center(self, centro_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("nombre", "direccion", "distrito", "telefono", "tipo")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            centro = self._find(data["centros"], centro_id)
            if centro is None:
                raise ValueError("El centro no existe")
            centro.update(
                {
                    "nombre": payload["nombre"].strip(),
                    "direccion": payload["direccion"].strip(),
                    "distrito": payload["distrito"].strip(),
                    "telefono": payload["telefono"].strip(),
                    "tipo": payload["tipo"].strip().upper(),
                }
            )
            self._write(data)
            return centro

    def create_patient(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("dni", "nombre", "telefono", "distrito")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            if any(p["dni"] == payload["dni"] for p in data["pacientes"]):
                raise ValueError("Ya existe un paciente con ese DNI")
            paciente = {
                "id": self._next_id(data["pacientes"]),
                "dni": payload["dni"].strip(),
                "nombre": payload["nombre"].strip(),
                "telefono": payload["telefono"].strip(),
                "obra_social": payload.get("obra_social", "Sin obra social").strip(),
                "distrito": payload["distrito"].strip(),
            }
            data["pacientes"].append(paciente)
            self._write(data)
            return paciente

    def update_patient(self, paciente_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("dni", "nombre", "telefono", "distrito")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            paciente = self._find(data["pacientes"], paciente_id)
            if paciente is None:
                raise ValueError("El paciente no existe")
            dni = payload["dni"].strip()
            if any(p["dni"] == dni and int(p["id"]) != int(paciente_id) for p in data["pacientes"]):
                raise ValueError("Ya existe otro paciente con ese DNI")
            paciente.update(
                {
                    "dni": dni,
                    "nombre": payload["nombre"].strip(),
                    "telefono": payload["telefono"].strip(),
                    "obra_social": payload.get("obra_social", "Sin obra social").strip(),
                    "distrito": payload["distrito"].strip(),
                }
            )
            self._write(data)
            return paciente

    def create_turno(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("paciente_id", "medico_id", "fecha", "hora", "motivo")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            medico = self._find(data["medicos"], int(payload["medico_id"]))
            if medico is None:
                raise ValueError("El medico seleccionado no existe")
            paciente = self._find(data["pacientes"], int(payload["paciente_id"]))
            if paciente is None:
                raise ValueError("El paciente seleccionado no existe")
            precio = payload.get("precio")
            if precio in (None, ""):
                precio = self._precio_estimado(data, medico)
            turno = {
                "id": self._next_id(data["turnos"]),
                "paciente_id": paciente["id"],
                "medico_id": medico["id"],
                "centro_id": medico["centro_id"],
                "fecha": payload["fecha"],
                "hora": payload["hora"],
                "estado": payload.get("estado", "PENDIENTE"),
                "precio": float(precio or 0),
                "motivo": payload["motivo"].strip(),
            }
            data["turnos"].append(turno)
            self._write(data)
            return self._enrich_turno(data, turno)

    def disponibilidad(self) -> list[dict[str, Any]]:
        data = self.read()
        rows: list[dict[str, Any]] = []
        for agenda in data["agendas"]:
            medico = self._find(data["medicos"], int(agenda["medico_id"]))
            if medico is None:
                continue
            tomados = sum(
                1
                for turno in data["turnos"]
                if int(turno["medico_id"]) == int(medico["id"])
                and turno["estado"] in {"PENDIENTE", "CONFIRMADO"}
            )
            item = deepcopy(agenda)
            item["medico"] = self._enrich_medico(data, medico)
            item["turnos_tomados"] = tomados
            item["cupos_libres"] = max(int(agenda["cupo_diario"]) - tomados, 0)
            item["precio_estimado"] = self._precio_estimado(data, medico)
            rows.append(item)
        return rows

    def update_turno(self, turno_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("paciente_id", "medico_id", "fecha", "hora", "motivo", "estado")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            turno = self._find(data["turnos"], turno_id)
            if turno is None:
                raise ValueError("El turno no existe")
            medico = self._find(data["medicos"], int(payload["medico_id"]))
            if medico is None:
                raise ValueError("El medico seleccionado no existe")
            paciente = self._find(data["pacientes"], int(payload["paciente_id"]))
            if paciente is None:
                raise ValueError("El paciente seleccionado no existe")
            turno.update(
                {
                    "paciente_id": paciente["id"],
                    "medico_id": medico["id"],
                    "centro_id": medico["centro_id"],
                    "fecha": payload["fecha"],
                    "hora": payload["hora"],
                    "estado": payload["estado"],
                    "precio": float(payload.get("precio", 0) or 0),
                    "motivo": payload["motivo"].strip(),
                }
            )
            self._write(data)
            return self._enrich_turno(data, turno)

    def delete_turno(self, turno_id: int) -> dict[str, Any]:
        with self._lock:
            data = self.read()
            turno = self._find(data["turnos"], turno_id)
            if turno is None:
                raise ValueError("El turno no existe")
            data["turnos"] = [t for t in data["turnos"] if int(t["id"]) != int(turno_id)]
            self._write(data)
            return self._enrich_turno(data, turno)

    def update_turno_estado(self, turno_id: int, estado: str) -> dict[str, Any]:
        estados_validos = {"PENDIENTE", "CONFIRMADO", "ATENDIDO", "CANCELADO", "AUSENTE"}
        if estado not in estados_validos:
            raise ValueError("Estado invalido")
        with self._lock:
            data = self.read()
            turno = self._find(data["turnos"], turno_id)
            if turno is None:
                raise ValueError("El turno no existe")
            turno["estado"] = estado
            self._write(data)
            return self._enrich_turno(data, turno)

    def save_document(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = ("paciente_id", "tipo", "nombre_archivo", "contenido_base64")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            paciente = self._find(data["pacientes"], int(payload["paciente_id"]))
            if paciente is None:
                raise ValueError("El paciente seleccionado no existe")
            file_name = self._safe_file_name(payload["nombre_archivo"])
            raw = payload["contenido_base64"]
            if "," in raw:
                raw = raw.split(",", 1)[1]
            bytes_data = base64.b64decode(raw)
            doc_id = self._next_id(data["documentos"])
            stored_name = f"paciente_{paciente['id']}_{doc_id}_{file_name}"
            target = self.uploads_dir / stored_name
            cached_content = None
            try:
                target.write_bytes(bytes_data)
                try:
                    stored_path = str(target.relative_to(ROOT))
                except ValueError:
                    stored_path = str(target)
            except OSError:
                stored_path = ""
                cached_content = raw
            doc = {
                "id": doc_id,
                "paciente_id": paciente["id"],
                "tipo": payload["tipo"].strip().upper(),
                "nombre_archivo": file_name,
                "mime_type": payload.get("mime_type") or mimetypes.guess_type(file_name)[0] or "application/octet-stream",
                "ruta": stored_path,
                "tamano_bytes": len(bytes_data),
            }
            if cached_content is not None:
                doc["contenido_base64"] = cached_content
            data["documentos"].append(doc)
            self._write(data)
            return self._enrich_documento(data, doc)

    def get_document(self, documento_id: int) -> dict[str, Any]:
        data = self.read()
        doc = self._find(data["documentos"], documento_id)
        if doc is None:
            raise ValueError("El documento no existe")
        item = self._enrich_documento(data, doc)
        content = doc.get("contenido_base64")
        if not content:
            path_value = doc.get("ruta", "")
            if not path_value:
                raise ValueError("El documento no tiene contenido disponible")
            path = Path(path_value)
            if not path.is_absolute():
                path = ROOT / path
            if not path.exists():
                raise ValueError("No se encontro el archivo guardado")
            content = base64.b64encode(path.read_bytes()).decode("ascii")
        item["contenido_base64"] = content
        item["data_url"] = f"data:{item.get('mime_type', 'application/octet-stream')};base64,{content}"
        return item

    def _write(self, data: dict[str, Any]) -> None:
        try:
            self.runtime_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self._memory_data = None
        except OSError:
            self._memory_data = deepcopy(data)

    @staticmethod
    def _require(payload: dict[str, Any], names: tuple[str, ...]) -> None:
        missing = [name for name in names if payload.get(name) in (None, "")]
        if missing:
            raise ValueError(f"Faltan campos: {', '.join(missing)}")

    @staticmethod
    def _next_id(rows: list[dict[str, Any]]) -> int:
        return max((int(row.get("id", 0)) for row in rows), default=0) + 1

    @staticmethod
    def _find(rows: list[dict[str, Any]], row_id: int) -> dict[str, Any] | None:
        return next((row for row in rows if int(row["id"]) == int(row_id)), None)

    @staticmethod
    def _safe_file_name(name: str) -> str:
        clean = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
        return clean or "documento.bin"

    def _enrich_medico(self, data: dict[str, Any], medico: dict[str, Any]) -> dict[str, Any]:
        item = deepcopy(medico)
        item["especialidad"] = self._find(data["especialidades"], medico["especialidad_id"])
        item["centro"] = self._find(data["centros"], medico["centro_id"])
        return item

    def _enrich_turno(self, data: dict[str, Any], turno: dict[str, Any]) -> dict[str, Any]:
        item = deepcopy(turno)
        item["paciente"] = self._find(data["pacientes"], turno["paciente_id"])
        item["medico"] = self._enrich_medico(data, self._find(data["medicos"], turno["medico_id"]))
        item["centro"] = self._find(data["centros"], turno["centro_id"])
        return item

    def _enrich_documento(self, data: dict[str, Any], doc: dict[str, Any]) -> dict[str, Any]:
        item = deepcopy(doc)
        item["paciente"] = self._find(data["pacientes"], doc["paciente_id"])
        return item

    def _precio_estimado(self, data: dict[str, Any], medico: dict[str, Any]) -> float:
        centro = self._find(data["centros"], int(medico["centro_id"]))
        if centro is None:
            return 0
        tarifa = next(
            (
                row
                for row in data["tarifas"]
                if int(row["especialidad_id"]) == int(medico["especialidad_id"])
                and row["tipo_centro"] == centro["tipo"]
            ),
            None,
        )
        return float(tarifa["precio"]) if tarifa else 0
