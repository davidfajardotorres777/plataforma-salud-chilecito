from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Sintoma:
    """Modelo de síntoma para MongoDB"""
    descripcion: str
    especialidad_id: str  # MongoDB ObjectId como string
    prioridad: str = "MEDIA"
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id_sintoma: Optional[str] = None  # MongoDB ObjectId como string
