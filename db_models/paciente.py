from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass(slots=True)
class Paciente:
    """Modelo de paciente para MongoDB"""
    dni: str
    nombre: str
    email: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    obra_social: Optional[str] = None
    distrito: Optional[str] = None
    centro_id: Optional[str] = None  # MongoDB ObjectId como string
    fecha_alta: datetime = field(default_factory=datetime.now)
    activo: bool = True
    id_paciente: Optional[str] = None  # MongoDB ObjectId como string
