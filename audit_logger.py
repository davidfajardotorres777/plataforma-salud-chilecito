"""
Módulo de auditoría y logs para Plataforma Salud Chilecito
===========================================================
Proporciona funcionalidad de logging y auditoría para todas las operaciones.

Características:
- Logging estructurado de todas las operaciones
- Auditoría de acciones de usuarios
- Logs de errores y excepciones
- Logs de rendimiento
- Logs de seguridad

Uso básico:
    from audit_logger import AuditLogger
    
    logger = AuditLogger()
    
    # Log de acción de usuario
    logger.log_action(
        usuario_id="user_123",
        accion="crear_turno",
        detalles={"paciente_id": "pac_456", "medico_id": "med_789"}
    )
    
    # Log de error
    logger.log_error(
        error="Error al conectar a MongoDB",
        contexto={"operacion": "listar_pacientes"}
    )
"""

import logging
import json
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class TipoLog(Enum):
    """Tipos de logs"""
    ACCION = "accion"
    ERROR = "error"
    SEGURIDAD = "seguridad"
    RENDIMIENTO = "rendimiento"
    SISTEMA = "sistema"


class NivelLog(Enum):
    """Niveles de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class AuditLogger:
    """
    Sistema de auditoría y logging para la plataforma.
    
    Proporciona métodos para registrar todas las operaciones
    importantes del sistema con contexto estructurado.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia del logger de auditoría.
        """
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura el logger de Python."""
        self.logger = logging.getLogger("salud_chilecito")
        self.logger.setLevel(logging.INFO)
        
        # Handler para archivo
        file_handler = logging.FileHandler("logs/audit.log")
        file_handler.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Agregar handlers
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def log_action(
        self,
        usuario_id: str,
        accion: str,
        detalles: Optional[Dict[str, Any]] = None,
        nivel: NivelLog = NivelLog.INFO
    ) -> bool:
        """
        Registra una acción de usuario.
        
        Args:
            usuario_id: ID del usuario
            accion: Acción realizada
            detalles: Detalles adicionales de la acción
            nivel: Nivel de log
        
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            log_entry = {
                "tipo": TipoLog.ACCION.value,
                "usuario_id": usuario_id,
                "accion": accion,
                "detalles": detalles or {},
                "timestamp": datetime.now().isoformat(),
                "nivel": nivel.value
            }
            
            self.logger.info(json.dumps(log_entry))
            return True
        except Exception as e:
            print(f"Error al loggear acción: {e}")
            return False
    
    def log_error(
        self,
        error: str,
        contexto: Optional[Dict[str, Any]] = None,
        nivel: NivelLog = NivelLog.ERROR
    ) -> bool:
        """
        Registra un error.
        
        Args:
            error: Mensaje de error
            contexto: Contexto del error
            nivel: Nivel de log
        
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            log_entry = {
                "tipo": TipoLog.ERROR.value,
                "error": error,
                "contexto": contexto or {},
                "timestamp": datetime.now().isoformat(),
                "nivel": nivel.value
            }
            
            self.logger.error(json.dumps(log_entry))
            return True
        except Exception as e:
            print(f"Error al loggear error: {e}")
            return False
    
    def log_security(
        self,
        evento: str,
        usuario_id: Optional[str] = None,
        detalles: Optional[Dict[str, Any]] = None,
        nivel: NivelLog = NivelLog.WARNING
    ) -> bool:
        """
        Registra un evento de seguridad.
        
        Args:
            evento: Evento de seguridad
            usuario_id: ID del usuario (opcional)
            detalles: Detalles adicionales
            nivel: Nivel de log
        
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            log_entry = {
                "tipo": TipoLog.SEGURIDAD.value,
                "evento": evento,
                "usuario_id": usuario_id,
                "detalles": detalles or {},
                "timestamp": datetime.now().isoformat(),
                "nivel": nivel.value
            }
            
            self.logger.warning(json.dumps(log_entry))
            return True
        except Exception as e:
            print(f"Error al loggear evento de seguridad: {e}")
            return False
    
    def log_performance(
        self,
        operacion: str,
        duracion_ms: float,
        detalles: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra una métrica de rendimiento.
        
        Args:
            operacion: Operación medida
            duracion_ms: Duración en milisegundos
            detalles: Detalles adicionales
        
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            log_entry = {
                "tipo": TipoLog.RENDIMIENTO.value,
                "operacion": operacion,
                "duracion_ms": duracion_ms,
                "detalles": detalles or {},
                "timestamp": datetime.now().isoformat(),
                "nivel": NivelLog.INFO.value
            }
            
            self.logger.info(json.dumps(log_entry))
            return True
        except Exception as e:
            print(f"Error al loggar rendimiento: {e}")
            return False
    
    def log_system(
        self,
        mensaje: str,
        detalles: Optional[Dict[str, Any]] = None,
        nivel: NivelLog = NivelLog.INFO
    ) -> bool:
        """
        Registra un evento del sistema.
        
        Args:
            mensaje: Mensaje del sistema
            detalles: Detalles adicionales
            nivel: Nivel de log
        
        Returns:
            bool: True si se registró exitosamente
        """
        try:
            log_entry = {
                "tipo": TipoLog.SISTEMA.value,
                "mensaje": mensaje,
                "detalles": detalles or {},
                "timestamp": datetime.now().isoformat(),
                "nivel": nivel.value
            }
            
            self.logger.info(json.dumps(log_entry))
            return True
        except Exception as e:
            print(f"Error al loggear evento del sistema: {e}")
            return False


# Instancia global del logger
audit_logger = AuditLogger()
