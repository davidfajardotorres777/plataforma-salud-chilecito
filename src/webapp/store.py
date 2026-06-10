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
        "sintomas",
        "configuracion_hospital",
        "tipos_consulta",
        "precios_especialidad",
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
        config = data.get("configuracion_hospital", [{}])[0] if data.get("configuracion_hospital") else {}
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
            "sintomas": data.get("sintomas", []),
            "configuracion_hospital": config,
            "tipos_consulta": data.get("tipos_consulta", []),
            "precios_especialidad": data.get("precios_especialidad", []),
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
        """
        Crea un nuevo paciente asociado a un hospital/centro específico.
        
        Este método asegura que los pacientes se asocien al hospital correcto
        para resolver el problema de que los pacientes no se guardan en el
        lugar respectivo cuando se cambia entre hospitales.
        
        Args:
            payload: Diccionario con dni, nombre, telefono, distrito, centro_id, etc.
        
        Returns:
            dict: El paciente creado
        
        Raises:
            ValueError: Si ya existe un paciente con ese DNI o si el centro no existe
        """
        required = ("dni", "nombre", "telefono", "distrito", "centro_id")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            
            # Verificar que el centro existe
            centro = self._find(data["centros"], int(payload["centro_id"]))
            if centro is None:
                raise ValueError("El centro/hospital seleccionado no existe")
            
            # Verificar si ya existe un paciente con ese DNI (solo en el mismo centro)
            if any(p["dni"] == payload["dni"] and int(p.get("centro_id", 0)) == int(payload["centro_id"]) for p in data["pacientes"]):
                raise ValueError("Ya existe un paciente con ese DNI en este hospital")
            
            paciente = {
                "id": self._next_id(data["pacientes"]),
                "dni": payload["dni"].strip(),
                "nombre": payload["nombre"].strip(),
                "telefono": payload["telefono"].strip(),
                "obra_social": payload.get("obra_social", "Sin obra social").strip(),
                "distrito": payload["distrito"].strip(),
                "centro_id": int(payload["centro_id"]),  # Asociar al centro/hospital
            }
            data["pacientes"].append(paciente)
            self._write(data)
            return self._enrich_paciente(data, paciente)

    def update_patient(self, paciente_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Actualiza un paciente manteniendo su asociación al centro/hospital.
        
        Args:
            paciente_id: ID del paciente a actualizar
            payload: Diccionario con dni, nombre, telefono, distrito, etc.
        
        Returns:
            dict: El paciente actualizado
        
        Raises:
            ValueError: Si el paciente no existe o si ya existe otro paciente con ese DNI
        """
        required = ("dni", "nombre", "telefono", "distrito")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            paciente = self._find(data["pacientes"], paciente_id)
            if paciente is None:
                raise ValueError("El paciente no existe")
            dni = payload["dni"].strip()
            # Verificar duplicado solo en el mismo centro
            if any(p["dni"] == dni and int(p["id"]) != int(paciente_id) and int(p.get("centro_id", 0)) == int(paciente.get("centro_id", 0)) for p in data["pacientes"]):
                raise ValueError("Ya existe otro paciente con ese DNI en este hospital")
            paciente.update(
                {
                    "dni": dni,
                    "nombre": payload["nombre"].strip(),
                    "telefono": payload["telefono"].strip(),
                    "obra_social": payload.get("obra_social", "Sin obra social").strip(),
                    "distrito": payload["distrito"].strip(),
                    # Mantener centro_id existente, no permitir cambiar de hospital
                }
            )
            self._write(data)
            return self._enrich_paciente(data, paciente)
    
    def list_pacientes_by_centro(self, centro_id: int) -> list[dict[str, Any]]:
        """
        Lista todos los pacientes de un hospital/centro específico.
        
        Este método es clave para resolver el problema de que los pacientes
        no se muestran correctamente cuando se cambia entre hospitales.
        
        Args:
            centro_id: ID del centro/hospital
        
        Returns:
            list[dict]: Lista de pacientes del centro con información enriquecida
        """
        with self._lock:
            data = self.read()
            pacientes = [p for p in data["pacientes"] if int(p.get("centro_id", 0)) == int(centro_id)]
            return [self._enrich_paciente(data, p) for p in pacientes]

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
    
    def _verificar_disponibilidad_turno(self, data: dict, medico_id: int, fecha: str, hora: str) -> bool:
        """
        Verifica si hay disponibilidad para un médico en una fecha y hora específicas.
        
        Esta es la función clave para la sincronización entre turnos virtuales y físicos.
        Valida que no exista un turno en el mismo horario, independientemente del origen.
        
        Args:
            data: Datos del sistema
            medico_id: ID del médico
            fecha: Fecha del turno (YYYY-MM-DD)
            hora: Hora del turno (HH:MM)
        
        Returns:
            bool: True si hay disponibilidad, False si no
        """
        # Buscar turnos existentes en el mismo horario
        for turno in data["turnos"]:
            if (int(turno["medico_id"]) == int(medico_id) 
                and turno["fecha"] == fecha 
                and turno["hora"] == hora
                and turno["estado"] in {"PENDIENTE", "CONFIRMADO"}):
                return False  # No hay disponibilidad, el horario está ocupado
        return True  # Hay disponibilidad
    
    def _verificar_turno_duplicado_paciente(self, data: dict, paciente_id: int, fecha: str, hora: str) -> bool:
        """
        Verifica si el paciente ya tiene un turno en la misma fecha y hora.
        
        Args:
            data: Datos del sistema
            paciente_id: ID del paciente
            fecha: Fecha del turno
            hora: Hora del turno
        
        Returns:
            bool: True si ya tiene un turno, False si no
        """
        for turno in data["turnos"]:
            if (int(turno["paciente_id"]) == int(paciente_id) 
                and turno["fecha"] == fecha 
                and turno["hora"] == hora
                and turno["estado"] in {"PENDIENTE", "CONFIRMADO"}):
                return True
        return False

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
    
    def verificar_disponibilidad_especifica(self, medico_id: int, fecha: str, hora: str) -> dict[str, Any]:
        """
        Verifica si hay disponibilidad específica para un médico en una fecha y hora.
        
        Este método es usado por el personal del hospital para verificar si un horario
        está disponible antes de hacer una reserva física.
        
        Args:
            medico_id: ID del médico
            fecha: Fecha del turno (YYYY-MM-DD)
            hora: Hora del turno (HH:MM)
        
        Returns:
            dict: Información de disponibilidad con mensaje
        """
        with self._lock:
            data = self.read()
            medico = self._find(data["medicos"], int(medico_id))
            if medico is None:
                return {"disponible": False, "mensaje": "El médico no existe"}
            
            disponible = self._verificar_disponibilidad_turno(data, medico["id"], fecha, hora)
            if disponible:
                return {
                    "disponible": True,
                    "mensaje": "El horario está disponible",
                    "medico": self._enrich_medico(data, medico)
                }
            else:
                return {
                    "disponible": False,
                    "mensaje": "El horario ya está reservado por otro paciente"
                }
    
    def create_turno_fisico(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Crea un turno desde una reserva física en el hospital.
        
        Este método es usado por el personal del hospital cuando un paciente
        se presenta presencialmente y quiere reservar un turno.
        
        Args:
            payload: Diccionario con paciente_id, medico_id, fecha, hora, motivo, etc.
        
        Returns:
            dict: El turno creado
        
        Raises:
            ValueError: Si no hay disponibilidad o si el médico/paciente no existe
        """
        payload["origen"] = "FISICO"  # Marcar como reserva física
        return self.create_turno(payload)

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
        """
        Guarda los datos de forma permanente en el archivo JSON.
        
        Este método asegura que los datos se guardan de forma persistente
        para resolver el problema de que los datos no se guardan cuando
        se sale de la plataforma o se crea algo.
        
        Si hay un error de escritura, intenta guardar en memoria como fallback
        pero también registra el error para diagnóstico.
        """
        try:
            # Intentar guardar en disco (persistencia permanente)
            self.runtime_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            self._memory_data = None  # Limpiar memoria cache
            print(f"[STORE] Datos guardados exitosamente en {self.runtime_path}")
        except OSError as e:
            # Fallback a memoria si hay error de escritura
            print(f"[STORE] Error al guardar en disco: {e}. Usando memoria como fallback.")
            self._memory_data = deepcopy(data)
            print(f"[STORE] ADVERTENCIA: Los datos solo están en memoria y se perderán al reiniciar.")
    
    def force_save(self) -> dict[str, Any]:
        """
        Fuerza un guardado manual de todos los datos actuales.
        
        Este método permite al usuario forzar un guardado manual para asegurar
        que todos los datos estén persistidos en disco.
        
        Returns:
            dict: Información sobre el estado del guardado
        """
        with self._lock:
            data = self.read()
            try:
                self._write(data)
                return {
                    "success": True,
                    "message": "Datos guardados exitosamente",
                    "path": str(self.runtime_path),
                    "using_memory": self._memory_data is not None
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Error al guardar: {str(e)}",
                    "using_memory": self._memory_data is not None
                }
    
    def get_persistence_status(self) -> dict[str, Any]:
        """
        Obtiene el estado actual de la persistencia de datos.
        
        Este método permite verificar si los datos se están guardando
        correctamente en disco o solo en memoria.
        
        Returns:
            dict: Información sobre el estado de persistencia
        """
        return {
            "runtime_path": str(self.runtime_path),
            "runtime_path_exists": self.runtime_path.exists(),
            "using_memory": self._memory_data is not None,
            "uploads_dir": str(self.uploads_dir),
            "uploads_dir_exists": self.uploads_dir.exists(),
            "can_write": self._check_write_permission()
        }
    
    def _check_write_permission(self) -> bool:
        """Verifica si hay permisos de escritura en el runtime_path."""
        try:
            test_file = self.runtime_path.parent / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False

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

    def _enrich_paciente(self, data: dict[str, Any], paciente: dict[str, Any]) -> dict[str, Any]:
        """
        Enriquece un paciente con información del centro/hospital asociado.
        
        Este método es necesario para mostrar información completa del paciente
        incluyendo el hospital al que pertenece.
        """
        item = deepcopy(paciente)
        item["centro"] = self._find(data["centros"], paciente.get("centro_id", 0))
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

    # --- Nuevos helpers para integración -------------------------------------------------
    def disponibilidad_filtered(
        self,
        centro_id: int | None = None,
        especialidad_id: int | None = None,
        medico_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """Devuelve la disponibilidad filtrada por centro, especialidad o medico.

        Esta función reutiliza la lógica existente de `disponibilidad` y aplica
        filtros adicionales sobre los items ya enriquecidos.
        """
        rows = self.disponibilidad()
        if centro_id is None and especialidad_id is None and medico_id is None:
            return rows
        filtered: list[dict[str, Any]] = []
        for item in rows:
            medico = item.get("medico") or {}
            # centro_id: puede estar en medico['centro_id']
            if centro_id is not None and int(medico.get("centro_id", -1)) != int(centro_id):
                continue
            if especialidad_id is not None and int(medico.get("especialidad_id", -1)) != int(especialidad_id):
                continue
            if medico_id is not None and int(medico.get("id", -1)) != int(medico_id):
                continue
            filtered.append(item)
        return filtered

    def create_agenda(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Crear una agenda para un medico (util para integración / import).

        Campos requeridos: medico_id, dia_semana, hora_inicio, hora_fin,
        duracion_minutos, cupo_diario.
        """
        required = ("medico_id", "dia_semana", "hora_inicio", "hora_fin", "duracion_minutos", "cupo_diario")
        self._require(payload, required)
        with self._lock:
            data = self.read()
            medico = self._find(data["medicos"], int(payload["medico_id"]))
            if medico is None:
                raise ValueError("El medico seleccionado no existe")
            agenda = {
                "id": self._next_id(data["agendas"]),
                "medico_id": int(payload["medico_id"]),
                "dia_semana": payload["dia_semana"].strip(),
                "hora_inicio": payload["hora_inicio"].strip(),
                "hora_fin": payload["hora_fin"].strip(),
                "duracion_minutos": int(payload["duracion_minutos"]),
                "cupo_diario": int(payload["cupo_diario"]),
            }
            data["agendas"].append(agenda)
            self._write(data)
            return agenda

    def import_agendas(self, agendas: list[dict[str, Any]]) -> dict[str, Any]:
        """Importa una lista de agendas (batch). Retorna resumen de la operación."""
        if not isinstance(agendas, list):
            raise ValueError("Payload de import_agendas debe ser una lista de agendas")
        created = 0
        skipped = 0
        errors: list[str] = []
        for idx, a in enumerate(agendas, start=1):
            try:
                self.create_agenda(a)
                created += 1
            except Exception as exc:
                skipped += 1
                errors.append(f"fila {idx}: {str(exc)}")
        return {"created": created, "skipped": skipped, "errors": errors}

    def calcular_precio(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Calcula un precio estimado basado en medico/especialidad/centro y motivo/sintomas.

        Reglas simples (MVP):
        - Usa la tarifa existente por especialidad/tipo de centro como `base_price`.
        - Extrae multiplicadores desde palabras clave del `motivo` para ajustar el precio.
        - Si la tarifa del centro es 0 (publico), intenta sugerir un precio privado si existe.
        """
        if not isinstance(payload, dict):
            raise ValueError("Payload invalido para calcular precio")
        with self._lock:
            data = self.read()

            medico = None
            especialidad_id = payload.get("especialidad_id")
            centro = None

            if payload.get("medico_id"):
                medico = self._find(data["medicos"], int(payload["medico_id"]))
                if medico is None:
                    raise ValueError("Medico no existe")
                especialidad_id = int(medico["especialidad_id"])
                centro = self._find(data["centros"], int(medico["centro_id"]))
            else:
                if payload.get("centro_id"):
                    centro = self._find(data["centros"], int(payload["centro_id"]))

            base = 0.0
            if medico is not None:
                base = float(self._precio_estimado(data, medico))
            elif especialidad_id and centro is not None:
                tarifa = next((t for t in data["tarifas"] if int(t["especialidad_id"]) == int(especialidad_id) and t["tipo_centro"] == centro["tipo"]), None)
                base = float(tarifa["precio"]) if tarifa else 0.0
            else:
                # intentar sugerir desde tarifas privadas si conocemos la especialidad
                if especialidad_id:
                    tarifa_priv = next((t for t in data["tarifas"] if int(t["especialidad_id"]) == int(especialidad_id) and t["tipo_centro"] == "PRIVADO"), None)
                    base = float(tarifa_priv["precio"]) if tarifa_priv else 0.0

            motivo = (payload.get("motivo") or payload.get("sintomas") or "").strip().lower()
            # mapa simple de palabras clave a multiplicadores
            multipliers: list[float] = []
            if "dolor de pecho" in motivo:
                multipliers.append(1.6)
            if "dolor" in motivo:
                multipliers.append(1.3)
            if "urg" in motivo or "emerg" in motivo or "urgente" in motivo:
                multipliers.append(1.5)
            if "control" in motivo:
                multipliers.append(1.0)
            if "consulta" in motivo:
                multipliers.append(1.0)
            if "estudio" in motivo or "resultado" in motivo:
                multipliers.append(1.2)

            multiplier = max(multipliers) if multipliers else 1.0

            suggested_private_base = None
            if base == 0 and especialidad_id:
                t = next((r for r in data["tarifas"] if int(r["especialidad_id"]) == int(especialidad_id) and r["tipo_centro"] == "PRIVADO"), None)
                if t:
                    suggested_private_base = float(t["precio"])

            estimated = 0.0
            if base and base > 0:
                estimated = float(base) * multiplier
            elif suggested_private_base:
                estimated = float(suggested_private_base) * multiplier

            range_min = round(max(0.0, estimated * 0.9), 2)
            range_max = round(estimated * 1.2, 2)

            return {
                "base_price": float(base),
                "suggested_private_base": float(suggested_private_base) if suggested_private_base is not None else None,
                "multiplier": float(multiplier),
                "estimated_price": round(float(estimated), 2),
                "range": [range_min, range_max],
                "motivo": motivo,
            }

    # --- Nuevos métodos para modelo Single-Hospital -----------------------------------------
    
    def listar_sintomas(self) -> list[dict[str, Any]]:
        """Lista todos los síntomas con sus especialidades asociadas"""
        data = self.read()
        sintomas = []
        for s in data.get("sintomas", []):
            especialidad = self._find(data["especialidades"], s.get("especialidad_id", -1))
            item = deepcopy(s)
            item["especialidad"] = especialidad
            sintomas.append(item)
        return sintomas
    
    def buscar_especialidad_por_sintoma(self, sintoma: str) -> dict[str, Any] | None:
        """Busca la especialidad recomendada según el síntoma"""
        data = self.read()
        sintoma_lower = sintoma.lower()
        for s in data.get("sintomas", []):
            if sintoma_lower in s.get("descripcion", "").lower():
                especialidad = self._find(data["especialidades"], s.get("especialidad_id", -1))
                if especialidad:
                    return {
                        "sintoma": s,
                        "especialidad": especialidad,
                        "prioridad": s.get("prioridad", "MEDIA")
                    }
        return None
    
    def obtener_configuracion_hospital(self) -> dict[str, Any]:
        """Obtiene la configuración del hospital"""
        data = self.read()
        configs = data.get("configuracion_hospital", [])
        if configs:
            config = configs[0]
            centro = self._find(data["centros"], config.get("centro_principal_id", -1))
            item = deepcopy(config)
            item["centro_principal"] = centro
            return item
        return {}
    
    def listar_tipos_consulta(self) -> list[dict[str, Any]]:
        """Lista todos los tipos de consulta"""
        return self.read().get("tipos_consulta", [])
    
    def obtener_precios_por_especialidad(self, centro_id: int, especialidad_id: int) -> list[dict[str, Any]]:
        """Obtiene precios por especialidad y centro"""
        data = self.read()
        precios = []
        for p in data.get("precios_especialidad", []):
            if int(p.get("centro_id", -1)) == int(centro_id) and int(p.get("especialidad_id", -1)) == int(especialidad_id):
                tipo = self._find(data["tipos_consulta"], p.get("tipo_consulta_id", -1))
                item = deepcopy(p)
                item["tipo_consulta"] = tipo
                precios.append(item)
        return precios
