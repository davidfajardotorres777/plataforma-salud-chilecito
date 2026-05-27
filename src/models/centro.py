from dataclasses import dataclass


@dataclass(slots=True)
class CentroSalud:
    nombre: str
    direccion: str
    distrito: str
    tipo: str
    telefono: str | None = None
    email: str | None = None
    activo: str = "S"
    id_centro: int | None = None
