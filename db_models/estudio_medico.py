from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoEstudio(Enum):
    """Tipos de estudios médicos"""
    LABORATORIO = "laboratorio"
    RADIOLOGIA = "radiologia"
    ECOGRAFIA = "ecografia"
    TOMOGRAFIA = "tomografia"
    RESONANCIA = "resonancia"
    ELECTROCARDIOGRAMA = "electrocardiograma"
    OTRO = "otro"


class EstadoEstudio(Enum):
    """Estados de un estudio médico"""
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADO = "completado"
    CANCELADO = "cancelado"


@dataclass(slots=True)
class EstudioMedico:
    """Modelo de estudio médico para MongoDB"""
    paciente_id: str  # MongoDB ObjectId como string
    medico_id: str  # MongoDB ObjectId como string
    tipo_estudio: TipoEstudio
    descripcion: str
    indicaciones: Optional[str] = None
    fecha_solicitud: datetime = field(default_factory=datetime.now)
    fecha_realizacion: Optional[datetime] = None
    fecha_resultado: Optional[datetime] = None
    resultado: Optional[str] = None
    estado: EstadoEstudio = EstadoEstudio.PENDIENTE
    archivo_url: Optional[str] = None
    turno_id: Optional[str] = None  # MongoDB ObjectId como string
    id_estudio: Optional[str] = None  # MongoDB ObjectId como string
