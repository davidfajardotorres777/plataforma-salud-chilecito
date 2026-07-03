import base64
import re
import unicodedata
from typing import Any, Callable
from .store import JsonStore

class BotAgent:
    def __init__(self, store: JsonStore):
        self.store = store
        self.valid_states = {"PENDIENTE", "CONFIRMADO", "ATENDIDO", "CANCELADO", "AUSENTE"}
        self.patient_aliases = {
            "nombre": ("nombre", "llamado", "paciente"),
            "dni": ("dni", "documento", "identificacion"),
            "telefono": ("telefono", "celular", "contacto"),
            "distrito": ("distrito", "barrio", "localidad", "zona", "ciudad", "pueblo", "lugar"),
            "obra_social": ("obra social", "cobertura", "prepaga", "mutuo", "os"),
            "centro_id": ("centro_id", "centro"),
        }
        self.turno_aliases = {
            "paciente_id": ("paciente", "para el paciente"),
            "medico_id": ("medico", "profesional", "doctor", "con el doctor"),
            "fecha": ("fecha", "el dia", "para el"),
            "hora": ("hora", "horario", "a las"),
            "motivo": ("motivo", "por", "razon", "consulta"),
            "estado": ("estado", "situacion", "condicion"),
            "precio": ("precio", "costo", "valor", "monto", "pagando"),
        }
        self.document_aliases = {
            "paciente_id": ("paciente", "del paciente"),
            "tipo": ("tipo", "categoria", "clasificacion", "clase"),
            "nombre_archivo": ("archivo", "fichero", "como"),
            "contenido": ("contenido", "dice", "texto", "informe", "nota"),
        }

    def handle(self, message: str) -> dict[str, Any]:
        normalized = self._normalize(message)
        if self._is_help(normalized):
            return self._help()
        elif self._wants_list(normalized):
            return self._handle_list(normalized)
        elif self._wants_create(normalized):
            return self._handle_create(normalized, message)
        elif self._wants_update(normalized):
            return self._handle_update(normalized, message)
        elif self._has_any(normalized, "eliminar", "borrar", "quitar", "cancelar turno", "anular turno"):
            return self._handle_delete(normalized)
        elif self._has_any(normalized, "confirmar", "atender", "ausente"):
            return self._handle_state_change(normalized)
        elif self._has_any(normalized, "ver", "leer", "abrir") and self._has_any(normalized, "documento", "estudio", "receta"):
            return self._view_document(normalized)
        elif self._has_any(normalized, "resumen", "dashboard", "metricas", "estadisticas"):
            return self._show_summary()
        elif self._mentions(normalized, "paciente", "turno", "documento"):
            return self._help("Entiendo que mencionas una de las entidades principales. ¿Que queres hacer?")
        else:
            return self._help("No entendi la consulta.")

    def _handle_list(self, normalized: str) -> dict[str, Any]:
        if self._mentions(normalized, "paciente", "pacientes"):
            rows = self.store.dashboard()["pacientes"]
            text = self._format_rows("Pacientes:", rows, lambda r: f"#{r['id']} {r['nombre']} (DNI: {r['dni']})")
            return self._reply(text, ["crear paciente nombre Ana dni 50111222"])
        elif self._mentions(normalized, "centro", "centros"):
            rows = self.store.dashboard()["centros"]
            text = self._format_rows("Centros:", rows, lambda r: f"#{r['id']} {r['nombre']} - {r['distrito']}")
            return self._reply(text, ["listar turnos"])
        elif self._mentions(normalized, "medico", "medicos", "profesional", "doctor"):
            rows = self.store.dashboard()["medicos"]
            text = self._format_rows("Medicos:", rows, lambda r: f"#{r['id']} {r['nombre']} - {r['especialidad']['nombre']}")
            return self._reply(text, ["crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30"])
        elif self._mentions(normalized, "turno", "turnos"):
            rows = self.store.dashboard()["turnos"]
            text = self._format_rows(
                "Turnos:", rows, lambda r: f"#{r['id']} {r['fecha']} {r['hora']} - {r['paciente']['nombre']} [{r['estado']}]"
            )
            return self._reply(text, ["listar pacientes", "listar medicos"])
        elif self._mentions(normalized, "documento", "estudio", "receta"):
            rows = self.store.dashboard()["documentos"]
            text = self._format_rows(
                "Documentos:", rows, lambda r: f"#{r['id']} {r['nombre_archivo']} - {r['paciente']['nombre']}"
            )
            return self._reply(text, ["crear documento paciente 1 tipo ESTUDIO contenido Resultado"])
        elif self._has_any(normalized, "disponible", "horario", "precio", "agenda"):
            return self._show_availability()
        else:
            return self._reply(
                "Que queres listar?", ["listar pacientes", "listar turnos", "listar centros", "listar documentos"]
            )

    def _handle_create(self, normalized: str, original: str) -> dict[str, Any]:
        try:
            if self._mentions(normalized, "documento", "estudio", "receta", "informe"):
                return self._create_text_document(original)
            elif self._mentions(normalized, "turno", "reserva", "cita"):
                return self._create_turno(original)
            elif self._mentions(normalized, "paciente"):
                return self._create_patient(original)
            else:
                return self._reply(
                    "No tengo claro que crear.",
                    ["crear paciente nombre Ana dni 50111222", "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30"],
                )
        except Exception as e:
            return self._reply(f"Error al crear: {str(e)}")

    def _handle_update(self, normalized: str, original: str) -> dict[str, Any]:
        try:
            if self._mentions(normalized, "turno", "reserva", "cita"):
                return self._update_turno(normalized, original)
            elif self._mentions(normalized, "paciente"):
                return self._update_patient(normalized, original)
            else:
                return self._reply("No tengo claro que editar. Ejemplo: editar paciente 1 telefono 3825-999000")
        except Exception as e:
            return self._reply(f"Error al actualizar: {str(e)}")

    def _handle_delete(self, normalized: str) -> dict[str, Any]:
        try:
            if self._mentions(normalized, "turno", "reserva", "cita"):
                return self._delete_turno(normalized)
            else:
                return self._reply("Solo puedo eliminar turnos por ahora. Ejemplo: eliminar turno 2")
        except Exception as e:
            return self._reply(f"Error al eliminar: {str(e)}")

    def _handle_state_change(self, normalized: str) -> dict[str, Any]:
        try:
            if "confirmar" in normalized:
                return self._change_turno_state(normalized, "CONFIRMADO")
            elif "atender" in normalized or "atendido" in normalized:
                return self._change_turno_state(normalized, "ATENDIDO")
            elif "ausente" in normalized:
                return self._change_turno_state(normalized, "AUSENTE")
            elif "cancelar" in normalized:
                return self._change_turno_state(normalized, "CANCELADO")
            else:
                return self._reply("Estado no reconocido para el turno.")
        except Exception as e:
            return self._reply(f"Error al cambiar estado: {str(e)}")

    def _show_summary(self) -> dict[str, Any]:
        dash = self.store.dashboard()
        m = dash["metricas"]
        reply = "\n".join(
            [
                "📊 Resumen de la plataforma:",
                f"- Pacientes: {m['pacientes']}",
                f"- Turnos (Total/Pendientes): {m['turnos']} / {m['turnos_pendientes']}",
                f"- Medicos: {m['medicos']}",
                f"- Documentos: {m['documentos']}",
                f"- Centros activos: {m['centros']}",
            ]
        )
        return self._reply(reply, self._default_suggestions())

    def _show_availability(self) -> dict[str, Any]:
        dash = self.store.dashboard()
        rows = dash["disponibilidad"]
        if not rows:
            return self._reply("No hay horarios disponibles configurados.", ["listar medicos"])
        lines = ["Disponibilidad por medico:"]
        for row in rows[:10]:
            lines.append(f"- {row['medico']['nombre']}: {row['dia_semana']} {row['hora_inicio']} a {row['hora_fin']} (${row['precio_estimado']})")
        return self._reply("\n".join(lines), ["crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30"])

    def _create_patient(self, text: str) -> dict[str, Any]:
        fields = self._extract_fields(text, self.patient_aliases)
        missing = self._missing(fields, ("dni", "nombre", "telefono", "distrito"))
        if missing:
            return self._need_fields(
                "paciente",
                missing,
                "crear paciente nombre Ana Diaz dni 50111222 telefono 3825-111222 distrito Chilecito obra social APOS centro 1",
            )
        patient = self.store.create_patient(
            {
                "dni": fields["dni"],
                "nombre": fields["nombre"],
                "telefono": fields["telefono"],
                "distrito": fields["distrito"],
                "obra_social": fields.get("obra_social", "Ninguna"),
                "centro_id": int(fields.get("centro_id", 1))
            }
        )
        return self._reply(
            f"Paciente creado: #{patient['id']} {patient['nombre']}.",
            ["listar pacientes", f"crear turno paciente {patient['id']} medico 1 fecha 2026-06-20 hora 09:30 motivo control"],
            {"paciente": patient},
        )

    def _update_patient(self, normalized: str, original: str) -> dict[str, Any]:
        patient_id = self._extract_id(normalized, "paciente")
        if patient_id is None:
            return self._reply("Necesito el id del paciente a editar. Ejemplo: editar paciente 1 telefono 3825-999000")
        current = self._find("pacientes", patient_id, "Paciente no encontrado.")
        fields = self._extract_fields(original, self.patient_aliases)
        payload: dict[str, Any] = {
            "dni": fields.get("dni", current["dni"]),
            "nombre": fields.get("nombre", current["nombre"]),
            "telefono": fields.get("telefono", current["telefono"]),
            "distrito": fields.get("distrito", current["distrito"]),
            "obra_social": fields.get("obra_social", current["obra_social"]),
        }
        updated = self.store.update_patient(patient_id, payload)
        return self._reply(
            f"Paciente actualizado: #{updated['id']} {updated['nombre']} (Telefono: {updated['telefono']}).",
            ["listar pacientes", f"editar paciente {updated['id']} distrito Chilecito"],
            {"paciente": updated},
        )

    def _create_turno(self, text: str) -> dict[str, Any]:
        fields = self._extract_fields(text, self.turno_aliases)
        missing = self._missing(fields, ("paciente_id", "medico_id", "fecha", "hora"))
        if missing:
            return self._need_fields(
                "turno",
                missing,
                "crear turno paciente 1 medico 1 fecha 2026-06-20 hora 09:30 motivo control",
            )
        turno = self.store.create_turno(self._turno_payload(fields))
        return self._reply(
            f"Turno creado: #{turno['id']} el {turno['fecha']} a las {turno['hora']} para {turno['paciente']['nombre']}.",
            ["listar turnos", f"confirmar turno {turno['id']}"],
            {"turno": turno},
        )

    def _update_turno(self, normalized: str, original: str) -> dict[str, Any]:
        turno_id = self._extract_id(normalized, "turno")
        if turno_id is None:
            return self._reply(
                "Necesito el id del turno a editar. Ejemplo: editar turno 1 fecha 2026-06-21 hora 10:00 motivo control reprogramado"
            )
        current = self._find("turnos", turno_id, "Turno no encontrado.")
        fields = self._extract_fields(original, self.turno_aliases)
        payload = self._turno_payload(fields, partial=True)
        for key, value in current.items():
            if key not in payload and key not in ("paciente", "medico", "id", "creado_en", "actualizado_en"):
                payload[key] = value
        if "paciente_id" not in payload:
            payload["paciente_id"] = current["paciente"]["id"]
        if "medico_id" not in payload:
            payload["medico_id"] = current["medico"]["id"]
        updated = self.store.update_turno(turno_id, payload)
        return self._reply(
            f"Turno actualizado: #{updated['id']} el {updated['fecha']} a las {updated['hora']} para {updated['paciente']['nombre']}.",
            ["listar turnos", f"eliminar turno {updated['id']}"],
            {"turno": updated},
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
        if "centro_id" in fields:
            payload["centro_id"] = self._as_int(fields["centro_id"], "centro")
        else:
            payload["centro_id"] = 1 # default
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
