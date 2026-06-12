from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Medico:
    """Modelo de médico para MongoDB"""
    nombre: str
    matricula: str
    especialidad_id: str  # MongoDB ObjectId como string
    centro_id: str  # MongoDB ObjectId como string
    telefono: Optional[str] = None
    email: Optional[str] = None
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id_medico: Optional[str] = None  # MongoDB ObjectId como string
