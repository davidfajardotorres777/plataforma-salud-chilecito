from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoInternacion(Enum):
    """Tipos de internación"""
    HOSPITALIZACION = "hospitalizacion"
    OBSERVACION = "observacion"
    CUIDADOS_INTENSIVOS = "cuidados_intensivos"
    CUIDADOS_INTERMEDIOS = "cuidados_intermedios"
    URGENCIA = "urgencia"


class EstadoInternacion(Enum):
    """Estados de una internación"""
    ACTIVA = "activa"
    ALTA_MEDICA = "alta_medica"
    TRASLADO = "traslado"
    FALLECIMIENTO = "fallecimiento"


@dataclass(slots=True)
class Internacion:
    """Modelo de internación para MongoDB"""
    paciente_id: str  # MongoDB ObjectId como string
    medico_id: str  # MongoDB ObjectId como string
    centro_id: str  # MongoDB ObjectId como string
    tipo: TipoInternacion
    motivo_ingreso: str
    diagnostico_ingreso: Optional[str] = None
    fecha_ingreso: datetime = field(default_factory=datetime.now)
    fecha_alta: Optional[datetime] = None
    estado: EstadoInternacion = EstadoInternacion.ACTIVA
    habitacion: Optional[str] = None
    cama: Optional[str] = None
    diagnostico_egreso: Optional[str] = None
    resumen_clinico: Optional[str] = None
    id_internacion: Optional[str] = None  # MongoDB ObjectId como string
