from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class AgendaMedico:
    """Modelo de agenda de médico para MongoDB"""
    medico_id: str  # MongoDB ObjectId como string
    dia_semana: str
    hora_inicio: str
    hora_fin: str
    duracion_minutos: int = 30
    cupo_diario: int = 16
    activa: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id_agenda: Optional[str] = None  # MongoDB ObjectId como string
