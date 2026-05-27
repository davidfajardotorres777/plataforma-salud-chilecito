from dataclasses import dataclass


@dataclass(slots=True)
class Especialidad:
    nombre: str
    descripcion: str | None = None
    activa: str = "S"
    id_especialidad: int | None = None
