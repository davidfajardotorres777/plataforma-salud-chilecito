from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class Paciente:
    dni: str
    nombre: str
    fecha_nacimiento: date | None = None
    telefono: str | None = None
    email: str | None = None
    obra_social: str | None = None
    distrito: str | None = None
    id_paciente: int | None = None
