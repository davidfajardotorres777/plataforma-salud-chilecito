from dataclasses import dataclass


@dataclass(slots=True)
class Medico:
    nombre: str
    matricula: str
    id_especialidad: int
    id_centro: int
    telefono: str | None = None
    email: str | None = None
    activo: str = "S"
    id_medico: int | None = None
