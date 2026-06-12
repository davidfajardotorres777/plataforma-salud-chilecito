from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class CentroSalud:
    """Modelo de centro de salud para MongoDB"""
    nombre: str
    direccion: str
    distrito: str
    tipo: str  # HOSPITAL, CLINICA, CENTRO_SALUD
    telefono: Optional[str] = None
    email: Optional[str] = None
    activo: bool = True
    fecha_creacion: datetime = field(default_factory=datetime.now)
    slug: Optional[str] = None
    id_centro: Optional[str] = None  # MongoDB ObjectId como string
