from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Turno:
    id_paciente: int
    id_medico: int
    id_centro: int
    fecha_turno: datetime
    estado: str = "PENDIENTE"
    precio_consulta: float = 0
    observaciones: str | None = None
    id_turno: int | None = None
