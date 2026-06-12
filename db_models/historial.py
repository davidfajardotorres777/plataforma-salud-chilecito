from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class HistorialClinico:
    """Modelo de historial clínico para MongoDB"""
    paciente_id: str  # MongoDB ObjectId como string
    diagnostico: Optional[str] = None
    indicaciones: Optional[str] = None
    profesional: Optional[str] = None
    turno_id: Optional[str] = None  # MongoDB ObjectId como string
    fecha_registro: datetime = field(default_factory=datetime.now)
    id_historial: Optional[str] = None  # MongoDB ObjectId como string
