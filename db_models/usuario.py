from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Rol(str, Enum):
    """Roles de usuario en el sistema"""
    PACIENTE = "paciente"
    ADMIN = "admin"
    MEDICO = "medico"


@dataclass(slots=True)
class Usuario:
    """Modelo de usuario para autenticación y autorización"""
    email: str
    password_hash: str
    rol: Rol
    nombre: str
    activo: bool = True
    verificado: bool = False
    fecha_registro: datetime = None
    fecha_verificacion: datetime = None
    verification_token: str = None
    id_usuario: str = None  # MongoDB ObjectId como string
    paciente_id: str = None  # Referencia al paciente si es rol PACIENTE
    medico_id: str = None  # Referencia al médico si es rol MEDICO
