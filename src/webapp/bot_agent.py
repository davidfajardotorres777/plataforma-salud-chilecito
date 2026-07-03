from __future__ import annotations

import base64
import re
import unicodedata
from typing import Any, Callable

from .store import JsonStore


class BotAgent:
    """Conversational operator for the Salud Chilecito demo.

    The bot is intentionally local and deterministic: it does not require API
    keys or internet access, but it performs real actions against the same
    JsonStore used by the browser platform.
    """

    patient_aliases = {
        "dni": ("dni", "documento"),
        "nombre": ("nombre", "nombre completo"),
        "telefono": ("telefono", "tel"),
        "distrito": ("distrito", "localidad"),
        "obra_social": ("obra social", "obrasocial", "obra", "mutual"),
    }
    center_aliases = {
        "nombre": ("nombre",),
        "direccion": ("direccion", "domicilio"),
        "distrito": ("distrito", "localidad"),
        "telefono": ("telefono", "tel"),
        "tipo": ("tipo",),
    }
    turno_aliases = {
        "paciente_id": ("paciente", "paciente id"),
        "medico_id": ("medico", "doctor", "profesional"),
        "fecha": ("fecha", "dia"),
        "hora": ("hora", "horario"),
        "motivo": ("motivo", "consulta"),
        "estado": ("estado",),
        "precio": ("precio", "costo"),
    }
    document_aliases = {
        "paciente_id": ("paciente", "paciente id"),
        "tipo": ("tipo",),
        "nombre_archivo": ("archivo", "nombre archivo", "nombre_archivo"),
        "contenido": ("contenido", "texto", "detalle"),
    }
    valid_states = {"PENDIENTE", "CONFIRMADO", "ATENDIDO", "CANCELADO", "AUSENTE"}

    def __init__(self, store: JsonStore):
        self.store = store

    def handle(self, message: str) -> dict[str, Any]:
        text = (message or "").strip()
        if not text:
            return self._help("Decime que queres hacer con la plataforma.")

        normalized = self._normalize(text)
        try:
            if self._is_help(normalized):
                return self._help()
            if self._has_any(normalized, "hola", "buenas", "buen dia"):
                return self._reply(
                    "Hola. Soy el bot IA de Salud Chilecito. Puedo crear, listar, editar y eliminar datos con comandos en lenguaje simple.",
                    ["listar pacientes", "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control", "ayuda"],
                )
            if self._has_any(normalized, "resumen", "dashboard", "metricas", "estado general"):
                return self._summary()
            if self._mentions(normalized, "documento", "documentos"):
                return self._document_intent(text, normalized)
            if self._mentions(normalized, "turno", "turnos", "agenda"):
                return self._turno_intent(text, normalized)
            if self._mentions(normalized, "centro", "centros"):
                return self._center_intent(text, normalized)
            if self._mentions(normalized, "paciente", "pacientes", "padron"):
                return self._patient_intent(text, normalized)
            if self._mentions(normalized, "medico", "medicos", "doctor", "doctores", "profesional"):
                return self._list_medicos()
            if self._mentions(normalized, "horarios", "disponibles", "precios", "disponibilidad"):
                return self._list_availability()
        except ValueError as exc:
            return self._reply(f"No pude completar la accion: {exc}", self._default_suggestions())

        return self._help(
            "No entendi todavia esa instruccion. Proba con una accion concreta como listar, crear, editar, eliminar o ver."
        )

    def _patient_intent(self, text: str, normalized: str) -> dict[str, Any]:
        if self._wants_list(normalized):
            return self._list_patients()
        if self._wants_update(normalized):
            return self._update_patient(text, normalized)
        if self._wants_create(normalized):
            return self._create_patient(text)
        return self._reply(
            "Puedo listar, crear o editar pacientes.",
            [
                "listar pacientes",
                "crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS",
                "editar paciente 1 telefono 3825-999000 distrito Nonogasta",
            ],
        )

    def _center_intent(self, text: str, normalized: str) -> dict[str, Any]:
        if self._wants_list(normalized):
            return self._list_centers()
        if self._wants_update(normalized):
            return self._update_center(text, normalized)
        if self._wants_create(normalized):
            return self._create_center(text)
        return self._reply(
            "Puedo listar, crear o editar centros de salud.",
            [
                "listar centros",
                "crear centro nombre Centro Demo direccion Calle 1 distrito Vichigasta telefono 3825-222333 tipo PUBLICO",
                "editar centro 1 telefono 3825-000111",
            ],
        )

    def _turno_intent(self, text: str, normalized: str) -> dict[str, Any]:
        if self._has_any(normalized, "eliminar", "borrar", "quitar", "sacar"):
            return self._delete_turno(normalized)
        if self._has_any(normalized, "cancelar") and not self._wants_create(normalized):
            return self._change_turno_state(normalized, "CANCELADO")
        if self._wants_update(normalized):
            return self._update_turno(text, normalized)
        if self._wants_create(normalized):
            return self._create_turno(text)
        if self._has_any(normalized, "confirmar"):
            return self._change_turno_state(normalized, "CONFIRMADO")
        if self._has_any(normalized, "atendido"):
            return self._change_turno_state(normalized, "ATENDIDO")
        if self._has_any(normalized, "ausente"):
            return self._change_turno_state(normalized, "AUSENTE")
        if self._has_any(normalized, "estado"):
            fields = self._extract_fields(text, self.turno_aliases)
            return self._change_turno_state(normalized, fields.get("estado", ""))
        if self._wants_list(normalized):
            return self._list_turnos()
        return self._reply(
            "Puedo listar, crear, editar, cambiar estado o eliminar turnos.",
            [
                "listar turnos",
                "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control",
                "editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado",
                "eliminar turno 2",
            ],
        )

    def _document_intent(self, text: str, normalized: str) -> dict[str, Any]:
        if self._wants_create(normalized) or self._has_any(normalized, "adjuntar", "guardar"):
            return self._create_text_document(text)
        if self._has_any(normalized, "ver", "abrir", "mostrar", "preview", "previsualizar") and self._extract_id(normalized, "documento") is not None:
            return self._view_document(normalized)
        if self._wants_list(normalized):
            return self._list_documents()
        if self._has_any(normalized, "ver", "abrir", "mostrar", "preview", "previsualizar"):
            return self._reply("Necesito el id del documento. Ejemplo: ver documento 1")
        return self._reply(
            "Puedo listar documentos, crear documentos de texto y abrir el contenido guardado.",
            [
                "listar documentos",
                "ver documento 1",
                "crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal",
            ],
        )

    def _summary(self) -> dict[str, Any]:
        dashboard = self.store.dashboard()
        metrics = dashboard["metricas"]
        reply = "\n".join(
            [
                "Resumen actual de la plataforma:",
                f"- Centros: {metrics['centros']}",
                f"- Pacientes: {metrics['pacientes']}",
                f"- Turnos pendientes: {metrics['turnos_pendientes']}",
                f"- Turnos confirmados: {metrics['turnos_confirmados']}",
                f"- Documentos: {metrics['documentos']}",
            ]
        )
        return self._reply(reply, ["listar turnos", "listar pacientes", "listar documentos"], {"metricas": metrics})

    def _list_patients(self) -> dict[str, Any]:
        patients = self.store.dashboard()["pacientes"]
        return self._reply(
            self._format_rows(
                "Pacientes registrados:",
                patients,
                lambda p: f"#{p['id']} {p['nombre']} | DNI {p['dni']} | {p['telefono']} | {p['distrito']} | {p.get('obra_social', '')}",
            ),
            ["editar paciente 1 telefono 3825-999000", "crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito"],
            {"items": patients},
        )

    def _list_centers(self) -> dict[str, Any]:
        centers = self.store.dashboard()["centros"]
        return self._reply(
            self._format_rows(
                "Centros de salud:",
                centers,
                lambda c: f"#{c['id']} {c['nombre']} | {c['distrito']} | {c['telefono']} | {c['tipo']}",
            ),
            ["editar centro 1 telefono 3825-000111", "crear centro nombre Centro Demo direccion Calle 1 distrito Vichigasta telefono 3825-222333 tipo PUBLICO"],
            {"items": centers},
        )

    def _list_medicos(self) -> dict[str, Any]:
        medicos = self.store.dashboard()["medicos"]
        return self._reply(
            self._format_rows(
                "Medicos disponibles:",
                medicos,
                lambda m: f"#{m['id']} {m['nombre']} | {m['especialidad']['nombre']} | {m['centro']['nombre']}",
            ),
            ["crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control", "listar turnos"],
            {"items": medicos},
        )

    def _list_availability(self) -> dict[str, Any]:
        disponibilidad = self.store.dashboard()["disponibilidad"]
        return self._reply(
            self._format_rows(
                "Disponibilidad por medico:",
                disponibilidad,
                lambda d: f"{d['medico']['nombre']} ({d['medico']['especialidad']['nombre']}): {d['dia_semana']} {d['hora_inicio']}-{d['hora_fin']} | ${d['precio_estimado']}",
            ),
            ["listar medicos", "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control"],
            {"items": disponibilidad},
        )

    def _list_turnos(self) -> dict[str, Any]:
        turnos = self.store.dashboard()["turnos"]
        return self._reply(
            self._format_rows(
                "Agenda de turnos:",
                turnos,
                lambda t: f"#{t['id']} {t['fecha']} {t['hora']} | {t['paciente']['nombre']} con {t['medico']['nombre']} | {t['estado']}",
            ),
            ["editar turno 1 fecha 2026-06-21 hora 10:00", "confirmar turno 1", "eliminar turno 2"],
            {"items": turnos},
        )

    def _list_documents(self) -> dict[str, Any]:
        docs = self.store.dashboard()["documentos"]
        return self._reply(
            self._format_rows(
                "Documentos guardados:",
                docs,
                lambda d: f"#{d['id']} {d['tipo']} | {d['nombre_archivo']} | paciente {d['paciente']['nombre']} | {d['tamano_bytes']} bytes",
            ),
            ["ver documento 1", "crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal"],
            {"items": docs},
        )

    def _create_patient(self, text: str) -> dict[str, Any]:
        fields = self._extract_fields(text, self.patient_aliases)
        missing = self._missing(fields, ("dni", "nombre", "telefono", "distrito"))
        if missing:
            return self._need_fields(
                "paciente",
                missing,
                "crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS",
            )
        patient = self.store.create_patient(
            {
                "dni": fields["dni"],
                "nombre": fields["nombre"],
                "telefono": fields["telefono"],
                "distrito": fields["distrito"],
                "obra_social": fields.get("obra_social", "Sin obra social"),
                "centro_id": 1,
            }
        )
        return self._reply(
            f"Paciente creado: #{patient['id']} {patient['nombre']} (DNI {patient['dni']}).",
            ["listar pacientes", f"crear turno paciente {patient['id']} medico 1 fecha 2026-06-20 hora 09:30 motivo control"],
            {"paciente": patient},
        )

    def _update_patient(self, text: str, normalized: str) -> dict[str, Any]:
        patient_id = self._extract_id(normalized, "paciente")
        if patient_id is None:
            return self._reply("Necesito el id del paciente. Ejemplo: editar paciente 1 telefono 3825-999000")
        fields = self._extract_fields(text, self.patient_aliases)
        if not fields:
            return self._reply("Decime que dato queres corregir. Ejemplo: editar paciente 1 telefono 3825-999000")
        current = self._find("pacientes", patient_id, "El paciente no existe")
        payload = {**current, **fields}
        patient = self.store.update_patient(patient_id, payload)
        return self._reply(
            f"Paciente actualizado: #{patient['id']} {patient['nombre']} | DNI {patient['dni']} | {patient['telefono']}.",
            ["listar pacientes", f"crear turno paciente {patient['id']} medico 1 fecha 2026-06-20 hora 09:30 motivo control"],
            {"paciente": patient},
        )

    def _create_center(self, text: str) -> dict[str, Any]:
        fields = self._extract_fields(text, self.center_aliases)
        missing = self._missing(fields, ("nombre", "direccion", "distrito", "telefono", "tipo"))
        if missing:
            return self._need_fields(
                "centro",
                missing,
                "crear centro nombre Centro Demo direccion Calle 1 distrito Vichigasta telefono 3825-222333 tipo PUBLICO",
            )
        center = self.store.create_center(fields)
        return self._reply(
            f"Centro creado: #{center['id']} {center['nombre']} ({center['distrito']}).",
            ["listar centros", f"editar centro {center['id']} telefono 3825-000111"],
            {"centro": center},
        )

    def _update_center(self, text: str, normalized: str) -> dict[str, Any]:
        center_id = self._extract_id(normalized, "centro")
        if center_id is None:
            return self._reply("Necesito el id del centro. Ejemplo: editar centro 1 telefono 3825-000111")
        fields = self._extract_fields(text, self.center_aliases)
        if not fields:
            return self._reply("Decime que dato queres corregir. Ejemplo: editar centro 1 direccion Av. Nueva 123")
        current = self._find("centros", center_id, "El centro no existe")
        payload = {**current, **fields}
        center = self.store.update_center(center_id, payload)
        return self._reply(
            f"Centro actualizado: #{center['id']} {center['nombre']} | {center['direccion']} | {center['telefono']}.",
            ["listar centros", "listar medicos"],
            {"centro": center},
        )

    def _create_turno(self, text: str) -> dict[str, Any]:
        fields = self._extract_fields(text, self.turno_aliases)
        missing = self._missing(fields, ("paciente_id", "medico_id", "fecha", "hora", "motivo"))
        if missing:
            return self._need_fields(
                "turno",
                missing,
                "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control",
            )
        payload = self._turno_payload(fields)
        turno = self.store.create_turno(payload)
        return self._reply(
            f"Turno creado: #{turno['id']} {turno['fecha']} {turno['hora']} para {turno['paciente']['nombre']} con {turno['medico']['nombre']}.",
            [f"confirmar turno {turno['id']}", f"editar turno {turno['id']} hora 10:00", "listar turnos"],
            {"turno": turno},
        )

    def _update_turno(self, text: str, normalized: str) -> dict[str, Any]:
        turno_id = self._extract_id(normalized, "turno")
        if turno_id is None:
            return self._reply("Necesito el id del turno. Ejemplo: editar turno 1 fecha 2026-06-21 hora 10:00")
        fields = self._extract_fields(text, self.turno_aliases)
        if not fields:
            return self._reply("Decime que dato queres modificar. Ejemplo: editar turno 1 fecha 2026-06-21 hora 10:00")
        current = self._find("turnos", turno_id, "El turno no existe")
        merged = {
            "paciente_id": current["paciente_id"],
            "medico_id": current["medico_id"],
            "fecha": current["fecha"],
            "hora": current["hora"],
            "motivo": current["motivo"],
            "estado": current["estado"],
            "precio": current.get("precio", 0),
        }
        merged.update(self._turno_payload(fields, partial=True))
        turno = self.store.update_turno(turno_id, merged)
        return self._reply(
            f"Turno actualizado: #{turno['id']} {turno['fecha']} {turno['hora']} | {turno['estado']} | {turno['motivo']}.",
            ["listar turnos", f"eliminar turno {turno['id']}"],
            {"turno": turno},
        )

    def _delete_turno(self, normalized: str) -> dict[str, Any]:
        turno_id = self._extract_id(normalized, "turno")
        if turno_id is None:
            return self._reply("Necesito el id del turno a eliminar. Ejemplo: eliminar turno 2")
        turno = self.store.delete_turno(turno_id)
        return self._reply(
            f"Turno eliminado de la agenda: #{turno['id']} {turno['fecha']} {turno['hora']} de {turno['paciente']['nombre']}.",
            ["listar turnos", "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control"],
            {"turno": turno},
        )

    def _change_turno_state(self, normalized: str, state: str) -> dict[str, Any]:
        turno_id = self._extract_id(normalized, "turno")
        if turno_id is None:
            return self._reply("Necesito el id del turno. Ejemplo: confirmar turno 1")
        final_state = self._state_value(state)
        turno = self.store.update_turno_estado(turno_id, final_state)
        return self._reply(
            f"Estado actualizado: turno #{turno['id']} quedo en {turno['estado']}.",
            ["listar turnos", f"editar turno {turno['id']} hora 10:00"],
            {"turno": turno},
        )

    def _create_text_document(self, text: str) -> dict[str, Any]:
        fields = self._extract_fields(text, self.document_aliases)
        missing = self._missing(fields, ("paciente_id", "tipo", "contenido"))
        if missing:
            return self._need_fields(
                "documento",
                missing,
                "crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal",
            )
        file_name = fields.get("nombre_archivo", "documento_bot.txt")
        content = fields["contenido"].encode("utf-8")
        document = self.store.save_document(
            {
                "paciente_id": self._as_int(fields["paciente_id"], "paciente"),
                "tipo": fields["tipo"],
                "nombre_archivo": file_name,
                "mime_type": "text/plain",
                "contenido_base64": base64.b64encode(content).decode("ascii"),
            }
        )
        preview = self.store.get_document(document["id"])
        return self._reply(
            f"Documento creado: #{document['id']} {document['nombre_archivo']} para {document['paciente']['nombre']}.",
            [f"ver documento {document['id']}", "listar documentos"],
            {"documento": preview},
        )

    def _view_document(self, normalized: str) -> dict[str, Any]:
        document_id = self._extract_id(normalized, "documento")
        if document_id is None:
            return self._reply("Necesito el id del documento. Ejemplo: ver documento 1")
        document = self.store.get_document(document_id)
        reply = "\n".join(
            [
                f"Documento #{document['id']}: {document['nombre_archivo']}",
                f"Tipo: {document['tipo']}",
                f"Paciente: {document['paciente']['nombre']}",
                f"MIME: {document['mime_type']}",
                f"Tamano: {document['tamano_bytes']} bytes",
            ]
        )
        return self._reply(reply, ["listar documentos"], {"documento": document})

    def _turno_payload(self, fields: dict[str, str], partial: bool = False) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if "paciente_id" in fields:
            payload["paciente_id"] = self._as_int(fields["paciente_id"], "paciente")
        if "medico_id" in fields:
            payload["medico_id"] = self._as_int(fields["medico_id"], "medico")
        for name in ("fecha", "hora", "motivo"):
            if name in fields:
                payload[name] = fields[name]
        if "estado" in fields:
            payload["estado"] = self._state_value(fields["estado"])
        elif not partial:
            payload["estado"] = "PENDIENTE"
        if "precio" in fields:
            payload["precio"] = float(fields["precio"].replace(",", "."))
        elif not partial:
            payload["precio"] = 0
        return payload

    def _find(self, collection: str, row_id: int, error: str) -> dict[str, Any]:
        rows = self.store.dashboard()[collection]
        found = next((row for row in rows if int(row["id"]) == int(row_id)), None)
        if found is None:
            raise ValueError(error)
        return found

    def _extract_fields(self, text: str, aliases: dict[str, tuple[str, ...]]) -> dict[str, str]:
        normalized = self._normalize(text)
        alias_to_key = {
            self._normalize(alias): key
            for key, values in aliases.items()
            for alias in values
        }
        pattern = re.compile(
            r"(?<!\w)(" + "|".join(re.escape(alias) for alias in sorted(alias_to_key, key=len, reverse=True)) + r")(?!\w)"
        )
        matches = [(match.start(), match.end(), alias_to_key[match.group(1)]) for match in pattern.finditer(normalized)]
        fields: dict[str, str] = {}
        for index, (start, end, key) in enumerate(matches):
            next_start = matches[index + 1][0] if index + 1 < len(matches) else len(text)
            value = text[end:next_start].strip(" \t\r\n:=,-;")
            value = re.sub(r"^(es|de|del|la|el)\s+", "", value, flags=re.IGNORECASE).strip(" \t\r\n:=,-;")
            if value:
                fields[key] = value
        return fields

    def _extract_id(self, normalized: str, entity: str) -> int | None:
        patterns = [
            rf"\b{entity}\s*(?:id\s*)?#?\s*(\d+)\b",
            r"\bid\s*#?\s*(\d+)\b",
            r"#\s*(\d+)\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, normalized)
            if match:
                return int(match.group(1))
        return None

    def _format_rows(self, title: str, rows: list[dict[str, Any]], formatter: Callable[[dict[str, Any]], str]) -> str:
        if not rows:
            return f"{title}\n- No hay registros cargados."
        lines = [title]
        for row in rows[:10]:
            lines.append(f"- {formatter(row)}")
        if len(rows) > 10:
            lines.append(f"- Y {len(rows) - 10} registros mas.")
        return "\n".join(lines)

    def _need_fields(self, entity: str, missing: list[str], example: str) -> dict[str, Any]:
        return self._reply(
            f"Para completar el {entity} me faltan estos datos: {', '.join(missing)}.\nEjemplo: {example}",
            [example],
        )

    def _help(self, intro: str = "Puedo manejar la plataforma por conversacion.") -> dict[str, Any]:
        return self._reply(
            "\n".join(
                [
                    intro,
                    "Comandos utiles:",
                    "- resumen",
                    "- listar pacientes / listar centros / listar medicos / listar turnos / listar documentos",
                    "- crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS",
                    "- editar paciente 1 telefono 3825-999000",
                    "- crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control",
                    "- editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado",
                    "- eliminar turno 2",
                    "- crear documento paciente 1 tipo ESTUDIO archivo resultado.txt contenido Resultado normal",
                    "- ver documento 1",
                ]
            ),
            self._default_suggestions(),
        )

    def _reply(
        self,
        reply: str,
        suggestions: list[str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = {"reply": reply, "suggestions": suggestions or []}
        if extra:
            payload.update(extra)
        return payload

    def _missing(self, fields: dict[str, str], names: tuple[str, ...]) -> list[str]:
        return [name for name in names if not fields.get(name)]

    def _as_int(self, value: str, label: str) -> int:
        match = re.search(r"\d+", value)
        if not match:
            raise ValueError(f"El id de {label} debe ser numerico")
        return int(match.group(0))

    def _state_value(self, state: str) -> str:
        normalized = self._normalize(state).upper()
        for value in self.valid_states:
            if self._normalize(value).upper() in normalized:
                return value
        raise ValueError("Estado invalido. Usar PENDIENTE, CONFIRMADO, ATENDIDO, CANCELADO o AUSENTE")

    def _wants_list(self, normalized: str) -> bool:
        return self._has_any(normalized, "listar", "lista", "mostrar", "ver todos", "consultar")

    def _wants_create(self, normalized: str) -> bool:
        return self._has_any(normalized, "crear", "agregar", "alta", "nuevo", "registrar", "reservar")

    def _wants_update(self, normalized: str) -> bool:
        return self._has_any(normalized, "editar", "modificar", "corregir", "actualizar", "cambiar", "reprogramar")

    def _is_help(self, normalized: str) -> bool:
        return normalized in {"ayuda", "help", "comandos", "que podes hacer"} or "como uso" in normalized

    def _mentions(self, normalized: str, *words: str) -> bool:
        return any(re.search(rf"\b{re.escape(word)}\b", normalized) for word in words)

    def _has_any(self, normalized: str, *needles: str) -> bool:
        return any(needle in normalized for needle in needles)

    def _default_suggestions(self) -> list[str]:
        return ["resumen", "listar pacientes", "listar turnos", "listar centros", "listar documentos"]

    def _normalize(self, text: str) -> str:
        lowered = text.lower()
        decomposed = unicodedata.normalize("NFD", lowered)
        return "".join(char for char in decomposed if not unicodedata.combining(char))
