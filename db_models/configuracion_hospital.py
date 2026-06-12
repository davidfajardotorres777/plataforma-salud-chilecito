from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class ConfiguracionHospital:
    """Modelo de configuración de hospital para MongoDB"""
    nombre_hospital: str
    centro_principal_id: str  # MongoDB ObjectId como string
    logo_url: Optional[str] = None
    color_primario: str = "#0066cc"
    color_secundario: str = "#ffffff"
    mensaje_bienvenida: Optional[str] = None
    requiere_derivacion: bool = False
    tiempo_cancelacion_horas: int = 24
    fecha_creacion: datetime = field(default_factory=datetime.now)
    id_configuracion: Optional[str] = None  # MongoDB ObjectId como string
