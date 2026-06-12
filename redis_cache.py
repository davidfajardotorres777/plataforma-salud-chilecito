"""
Módulo de caché Redis para Plataforma Salud Chilecito
=====================================================
Proporciona funcionalidad de caché y gestión de sesiones con Redis.

Características:
- Caché de datos frecuentemente accedidos
- Gestión de sesiones de usuario
- Almacenamiento temporal de tokens
- TTL (Time To Live) automático

Uso básico:
    from redis_cache import RedisCache
    
    cache = RedisCache()
    
    # Guardar valor en caché
    cache.set("centros", centros_list, ttl=3600)
    
    # Obtener valor de caché
    centros = cache.get("centros")
    
    # Guardar sesión
    cache.set_session("user_123", session_data, ttl=86400)
    
    # Obtener sesión
    session = cache.get_session("user_123")
    
    cache.cerrar()
"""

import json
from typing import Optional, Any, Dict
from datetime import timedelta

from config_vars import get_redis_config


class RedisCache:
    """
    Cliente de caché Redis para la plataforma.
    
    Proporciona métodos para almacenar y recuperar datos
    con soporte para TTL (Time To Live).
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia del cliente Redis.
        """
        config = get_redis_config()
        self._config = config
        self._client = None
    
    def _get_client(self):
        """Obtiene el cliente de Redis (lazy loading)."""
        if self._client is None:
            try:
                import redis
                config = self._config
                
                # Crear cliente Redis
                if config["password"]:
                    self._client = redis.Redis(
                        host=config["host"],
                        port=config["port"],
                        db=config["db"],
                        password=config["password"],
                        decode_responses=True
                    )
                else:
                    self._client = redis.Redis(
                        host=config["host"],
                        port=config["port"],
                        db=config["db"],
                        decode_responses=True
                    )
            except ImportError:
                raise RuntimeError(
                    "Falta instalar redis. Ejecuta: pip install redis"
                )
        return self._client
    
    def ping(self) -> str:
        """
        Verifica la conexión con Redis.
        
        Returns:
            str: "OK" si la conexión funciona, "SIN_RESPUESTA" en caso contrario
        """
        try:
            client = self._get_client()
            client.ping()
            return "OK"
        except Exception:
            return "SIN_RESPUESTA"
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Guarda un valor en caché.
        
        Args:
            key: Clave del valor
            value: Valor a guardar (será serializado a JSON)
            ttl: Tiempo de vida en segundos (opcional)
        
        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            client = self._get_client()
            serialized = json.dumps(value, default=str)
            
            if ttl:
                return client.setex(key, ttl, serialized)
            else:
                return client.set(key, serialized)
        except Exception as e:
            print(f"Error al guardar en caché: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor de caché.
        
        Args:
            key: Clave del valor
        
        Returns:
            any | None: Valor deserializado si existe
        """
        try:
            client = self._get_client()
            serialized = client.get(key)
            
            if serialized:
                return json.loads(serialized)
            return None
        except Exception as e:
            print(f"Error al obtener de caché: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Elimina un valor de caché.
        
        Args:
            key: Clave del valor
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            client = self._get_client()
            return client.delete(key) > 0
        except Exception as e:
            print(f"Error al eliminar de caché: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Verifica si una clave existe en caché.
        
        Args:
            key: Clave a verificar
        
        Returns:
            bool: True si la clave existe
        """
        try:
            client = self._get_client()
            return client.exists(key) > 0
        except Exception as e:
            print(f"Error al verificar existencia: {e}")
            return False
    
    def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 86400) -> bool:
        """
        Guarda datos de sesión de usuario.
        
        Args:
            session_id: ID de la sesión
            data: Datos de la sesión
            ttl: Tiempo de vida en segundos (default: 24 horas)
        
        Returns:
            bool: True si se guardó exitosamente
        """
        return self.set(f"session:{session_id}", data, ttl)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos de sesión de usuario.
        
        Args:
            session_id: ID de la sesión
        
        Returns:
            dict | None: Datos de la sesión si existe
        """
        return self.get(f"session:{session_id}")
    
    def delete_session(self, session_id: str) -> bool:
        """
        Elimina una sesión de usuario.
        
        Args:
            session_id: ID de la sesión
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        return self.delete(f"session:{session_id}")
    
    def invalidate_user_sessions(self, user_id: str) -> bool:
        """
        Invalida todas las sesiones de un usuario.
        
        Args:
            user_id: ID del usuario
        
        Returns:
            bool: True si se invalidaron exitosamente
        """
        try:
            client = self._get_client()
            pattern = f"session:*"
            keys = client.keys(pattern)
            
            deleted = 0
            for key in keys:
                session_data = self.get(key.replace("session:", ""))
                if session_data and session_data.get("usuario_id") == user_id:
                    if client.delete(key):
                        deleted += 1
            
            return deleted > 0
        except Exception as e:
            print(f"Error al invalidar sesiones: {e}")
            return False
    
    def clear_all(self) -> bool:
        """
        Limpia toda la caché.
        
        Returns:
            bool: True si se limpió exitosamente
        """
        try:
            client = self._get_client()
            client.flushdb()
            return True
        except Exception as e:
            print(f"Error al limpiar caché: {e}")
            return False
    
    def cerrar(self):
        """Cierra la conexión con Redis."""
        if self._client is not None:
            self._client.close()
            self._client = None
