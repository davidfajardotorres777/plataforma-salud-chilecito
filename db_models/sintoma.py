from dataclasses import dataclass


@dataclass(slots=True)
class Sintoma:
    descripcion: str
    id_especialidad: int
    prioridad: str = "MEDIA"
    activo: str = "S"
    id_sintoma: int | None = None
