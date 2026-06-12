from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Turno:
    """Modelo de turno para MongoDB"""
    paciente_id: str  # MongoDB ObjectId como string
    medico_id: str  # MongoDB ObjectId como string
    centro_id: str  # MongoDB ObjectId como string
    fecha_turno: datetime
    estado: str = "PENDIENTE"
    precio_consulta: float = 0
    observaciones: Optional[str] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id_turno: Optional[str] = None  # MongoDB ObjectId como string
