"""
Sistema de autenticación y autorización para Salud Chilecito.

Soporta:
- API Keys para integración con sistemas externos (HIS)
- JWT tokens para autenticación de usuarios
- Roles y permisos
- Logs de auditoría
"""

import secrets
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path


class APIKeyManager:
    """Gestión de API Keys para integración con sistemas externos."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("runtime/api_keys.json")
        self.keys = self._load_keys()
    
    def _load_keys(self) -> Dict:
        """Carga las API Keys desde el almacenamiento."""
        if self.storage_path.exists():
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        return {}
    
    def _save_keys(self) -> None:
        """Guarda las API Keys en el almacenamiento."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self.keys, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def generate_key(self, hospital_name: str, hospital_id: int, permissions: List[str] = None) -> str:
        """
        Genera una nueva API Key para un hospital.
        
        Args:
            hospital_name: Nombre del hospital
            hospital_id: ID del hospital en el sistema
            permissions: Lista de permisos (ej: ["read:turnos", "write:turnos"])
        
        Returns:
            API Key generada (formato: sk_hospital_timestamp_random)
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = secrets.token_hex(16)
        key = f"sk_{hospital_name.lower().replace(' ', '_')}_{timestamp}_{random_part}"
        
        # Hash de la key para almacenamiento seguro
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        self.keys[key_hash] = {
            "hospital_name": hospital_name,
            "hospital_id": hospital_id,
            "permissions": permissions or ["read", "write"],
            "created_at": datetime.now().isoformat(),
            "last_used": None,
            "is_active": True
        }
        
        self._save_keys()
        return key
    
    def validate_key(self, api_key: str) -> Optional[Dict]:
        """
        Valida una API Key y retorna la información del hospital.
        
        Args:
            api_key: API Key a validar
        
        Returns:
            Diccionario con información del hospital si la key es válida, None en caso contrario
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.keys:
            return None
        
        key_data = self.keys[key_hash]
        
        if not key_data["is_active"]:
            return None
        
        # Actualizar last_used
        key_data["last_used"] = datetime.now().isoformat()
        self._save_keys()
        
        return {
            "hospital_name": key_data["hospital_name"],
            "hospital_id": key_data["hospital_id"],
            "permissions": key_data["permissions"]
        }
    
    def revoke_key(self, api_key: str) -> bool:
        """
        Revoca una API Key.
        
        Args:
            api_key: API Key a revocar
        
        Returns:
            True si se revocó correctamente, False en caso contrario
        """
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        if key_hash not in self.keys:
            return False
        
        self.keys[key_hash]["is_active"] = False
        self.keys[key_hash]["revoked_at"] = datetime.now().isoformat()
        self._save_keys()
        return True
    
    def list_keys(self, hospital_id: Optional[int] = None) -> List[Dict]:
        """
        Lista las API Keys (sin mostrar el valor completo por seguridad).
        
        Args:
            hospital_id: Filtrar por hospital_id (opcional)
        
        Returns:
            Lista de API Keys con información segura
        """
        keys_list = []
        
        for key_hash, key_data in self.keys.items():
            if hospital_id and key_data["hospital_id"] != hospital_id:
                continue
            
            # Mostrar solo los primeros 8 caracteres del hash
            safe_key = f"sk_...{key_hash[:8]}"
            
            keys_list.append({
                "key": safe_key,
                "hospital_name": key_data["hospital_name"],
                "hospital_id": key_data["hospital_id"],
                "permissions": key_data["permissions"],
                "created_at": key_data["created_at"],
                "last_used": key_data["last_used"],
                "is_active": key_data["is_active"]
            })
        
        return keys_list


class PermissionManager:
    """Gestión de permisos y roles."""
    
    # Definición de permisos disponibles
    PERMISSIONS = {
        # Turnos
        "read:turnos": "Leer turnos",
        "write:turnos": "Crear turnos",
        "update:turnos": "Actualizar turnos",
        "delete:turnos": "Eliminar turnos",
        
        # Pacientes
        "read:pacientes": "Leer pacientes",
        "write:pacientes": "Crear pacientes",
        "update:pacientes": "Actualizar pacientes",
        
        # Médicos
        "read:medicos": "Leer médicos",
        "write:medicos": "Crear médicos",
        "update:medicos": "Actualizar médicos",
        
        # Especialidades
        "read:especialidades": "Leer especialidades",
        "write:especialidades": "Crear especialidades",
        
        # Agendas
        "read:agendas": "Leer agendas",
        "write:agendas": "Crear agendas",
        "update:agendas": "Actualizar agendas",
        
        # Documentos
        "read:documentos": "Leer documentos",
        "write:documentos": "Subir documentos",
        
        # Configuración
        "read:config": "Leer configuración",
        "write:config": "Actualizar configuración",
        
        # Síntomas
        "read:sintomas": "Leer síntomas",
        "write:sintomas": "Crear síntomas",
        
        # Precios
        "read:precios": "Leer precios",
        "write:precios": "Actualizar precios"
    }
    
    # Roles predefinidos
    ROLES = {
        "admin": list(PERMISSIONS.keys()),  # Todos los permisos
        "hospital": [
            "read:turnos", "write:turnos", "update:turnos",
            "read:pacientes", "write:pacientes", "update:pacientes",
            "read:medicos", "read:especialidades",
            "read:agendas", "write:agendas", "update:agendas",
            "read:documentos", "write:documentos",
            "read:config", "write:config",
            "read:sintomas", "write:sintomas",
            "read:precios", "write:precios"
        ],
        "paciente": [
            "read:turnos", "write:turnos",
            "read:pacientes", "update:pacientes",
            "read:medicos", "read:especialidades",
            "read:agendas",
            "read:documentos", "write:documentos",
            "read:sintomas", "read:precios"
        ],
        "integracion": [
            "read:turnos", "write:turnos", "update:turnos",
            "read:pacientes", "write:pacientes", "update:pacientes",
            "read:medicos", "read:especialidades",
            "read:agendas", "write:agendas", "update:agendas",
            "read:config"
        ]
    }
    
    @classmethod
    def has_permission(cls, permissions: List[str], required_permission: str) -> bool:
        """
        Verifica si un conjunto de permisos incluye el permiso requerido.
        
        Args:
            permissions: Lista de permisos del usuario/rol
            required_permission: Permiso requerido
        
        Returns:
            True si tiene el permiso, False en caso contrario
        """
        return required_permission in permissions
    
    @classmethod
    def get_role_permissions(cls, role: str) -> List[str]:
        """
        Obtiene los permisos de un rol.
        
        Args:
            role: Nombre del rol
        
        Returns:
            Lista de permisos del rol
        """
        return cls.ROLES.get(role, [])


class AuditLogger:
    """Sistema de logs de auditoría para operaciones de API."""
    
    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or Path("runtime/audit.log")
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, event_type: str, api_key: str, hospital_id: int, 
            endpoint: str, method: str, status: int, 
            details: Optional[Dict] = None) -> None:
        """
        Registra un evento de auditoría.
        
        Args:
            event_type: Tipo de evento (ej: "api_call", "key_created", "key_revoked")
            api_key: API Key utilizada (hash seguro)
            hospital_id: ID del hospital
            endpoint: Endpoint de la API
            method: Método HTTP
            status: Código de estado HTTP
            details: Detalles adicionales (opcional)
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "api_key_hash": hashlib.sha256(api_key.encode()).hexdigest()[:16],
            "hospital_id": hospital_id,
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "details": details or {}
        }
        
        # Escribir en el log
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_logs(self, hospital_id: Optional[int] = None, 
                 event_type: Optional[str] = None,
                 limit: int = 100) -> List[Dict]:
        """
        Obtiene logs de auditoría con filtros opcionales.
        
        Args:
            hospital_id: Filtrar por hospital_id (opcional)
            event_type: Filtrar por tipo de evento (opcional)
            limit: Límite de registros a retornar
        
        Returns:
            Lista de logs
        """
        if not self.log_path.exists():
            return []
        
        logs = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                log = json.loads(line)
                
                if hospital_id and log.get("hospital_id") != hospital_id:
                    continue
                
                if event_type and log.get("event_type") != event_type:
                    continue
                
                logs.append(log)
                
                if len(logs) >= limit:
                    break
        
        return logs


# Instancias globales
api_key_manager = APIKeyManager()
permission_manager = PermissionManager()
audit_logger = AuditLogger()
