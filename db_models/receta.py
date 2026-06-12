from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass(slots=True)
class MedicamentoRecetado:
    """Modelo de medicamento en una receta"""
    nombre: str
    dosis: str
    frecuencia: str
    duracion: str
    instrucciones: Optional[str] = None


@dataclass(slots=True)
class Receta:
    """Modelo de receta médica para MongoDB"""
    paciente_id: str  # MongoDB ObjectId como string
    medico_id: str  # MongoDB ObjectId como string
    turno_id: Optional[str] = None  # MongoDB ObjectId como string
    medicamentos: List[MedicamentoRecetado] = field(default_factory=list)
    diagnostico: Optional[str] = None
    indicaciones: Optional[str] = None
    fecha_emision: datetime = field(default_factory=datetime.now)
    activa: bool = True
    id_receta: Optional[str] = None  # MongoDB ObjectId como string
