from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class TipoNotificacion(Enum):
    """Tipos de notificaciones"""
    TURNO_CONFIRMADO = "turno_confirmado"
    TURNO_CANCELADO = "turno_cancelado"
    TURNO_RECORDATORIO = "turno_recordatorio"
    RECETA_DISPONIBLE = "receta_disponible"
    ESTUDIO_LISTO = "estudio_listo"
    RESULTADO_LABORATORIO = "resultado_laboratorio"
    MENSAJE_MEDICO = "mensaje_medico"
    PROMOCION = "promocion"
    SISTEMA = "sistema"


class EstadoNotificacion(Enum):
    """Estados de una notificación"""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    LEIDA = "leida"
    FALLIDA = "fallida"


@dataclass(slots=True)
class Notificacion:
    """Modelo de notificación para MongoDB"""
    usuario_id: str  # MongoDB ObjectId como string
    tipo: TipoNotificacion
    titulo: str
    mensaje: str
    estado: EstadoNotificacion = EstadoNotificacion.PENDIENTE
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_envio: Optional[datetime] = None
    fecha_lectura: Optional[datetime] = None
    metadata: Optional[dict] = None
    id_notificacion: Optional[str] = None  # MongoDB ObjectId como string
