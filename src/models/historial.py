from dataclasses import dataclass


@dataclass(slots=True)
class HistorialClinico:
    id_paciente: int
    diagnostico: str | None = None
    indicaciones: str | None = None
    profesional: str | None = None
    id_turno: int | None = None
    id_historial: int | None = None
