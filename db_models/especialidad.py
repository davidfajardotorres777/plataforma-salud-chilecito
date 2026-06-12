from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Especialidad:
    """Modelo de especialidad para MongoDB"""
    nombre: str
    descripcion: Optional[str] = None
    activa: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id_especialidad: Optional[str] = None  # MongoDB ObjectId como string
