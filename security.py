"""
Módulo de seguridad para Plataforma Salud Chilecito
==================================================
Proporciona funcionalidad de seguridad avanzada.

Características:
- Rate limiting
- Validación de tokens
- Sanitización de inputs
- Protección contra CSRF
- Validación de contraseñas

Uso básico:
    from security import SecurityManager
    
    security = SecurityManager()
    
    # Validar contraseña
    if security.validar_contrasena("MiPassword123!"):
        print("Contraseña válida")
    
    # Sanitizar input
    input_sanitizado = security.sanitizar_input("<script>alert('xss')</script>")
"""

import re
import secrets
from typing import Optional, List
from datetime import datetime, timedelta
from functools import wraps


class SecurityManager:
    """
    Gestor de seguridad para la plataforma.
    
    Proporciona métodos para validar y sanitizar datos,
    proteger contra ataques comunes y gestionar la seguridad.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia del gestor de seguridad.
        """
        self._rate_limits = {}
    
    def validar_contrasena(self, password: str) -> tuple[bool, List[str]]:
        """
        Valida la fortaleza de una contraseña.
        
        Args:
            password: Contraseña a validar
        
        Returns:
            tuple: (es_valida, lista_errores)
        """
        errores = []
        
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres")
        
        if not re.search(r'[A-Z]', password):
            errores.append("La contraseña debe contener al menos una mayúscula")
        
        if not re.search(r'[a-z]', password):
            errores.append("La contraseña debe contener al menos una minúscula")
        
        if not re.search(r'[0-9]', password):
            errores.append("La contraseña debe contener al menos un número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errores.append("La contraseña debe contener al menos un carácter especial")
        
        return len(errores) == 0, errores
    
    def sanitizar_input(self, input_str: str) -> str:
        """
        Sanitiza un input para prevenir XSS.
        
        Args:
            input_str: Input a sanitizar
        
        Returns:
            str: Input sanitizado
        """
        if not input_str:
            return ""
        
        # Escapar caracteres HTML peligrosos
        sanitizado = input_str
        sanitizado = sanitizado.replace("&", "&amp;")
        sanitizado = sanitizado.replace("<", "&lt;")
        sanitizado = sanitizado.replace(">", "&gt;")
        sanitizado = sanitizado.replace('"', "&quot;")
        sanitizado = sanitizado.replace("'", "&#x27;")
        sanitizado = sanitizado.replace("/", "&#x2F;")
        
        return sanitizado
    
    def validar_email(self, email: str) -> bool:
        """
        Valida un email.
        
        Args:
            email: Email a validar
        
        Returns:
            bool: True si el email es válido
        """
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(patron, email) is not None
    
    def validar_dni(self, dni: str) -> bool:
        """
        Valida un DNI argentino.
        
        Args:
            dni: DNI a validar
        
        Returns:
            bool: True si el DNI es válido
        """
        # Eliminar espacios y puntos
        dni_limpio = dni.replace(" ", "").replace(".", "")
        
        # Debe ser numérico y tener entre 7 y 8 dígitos
        return dni_limpio.isdigit() and 7 <= len(dni_limpio) <= 8
    
    def validar_telefono(self, telefono: str) -> bool:
        """
        Valida un teléfono argentino.
        
        Args:
            telefono: Teléfono a validar
        
        Returns:
            bool: True si el teléfono es válido
        """
        # Eliminar espacios, guiones y paréntesis
        telefono_limpio = telefono.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Debe ser numérico y tener entre 8 y 13 dígitos (con código de país)
        return telefono_limpio.isdigit() and 8 <= len(telefono_limpio) <= 13
    
    def generar_token_seguro(self, longitud: int = 32) -> str:
        """
        Genera un token seguro.
        
        Args:
            longitud: Longitud del token
        
        Returns:
            str: Token seguro
        """
        return secrets.token_urlsafe(longitud)
    
    def verificar_rate_limit(self, identificador: str, limite: int = 100, ventana_segundos: int = 60) -> bool:
        """
        Verifica si un identificador ha excedido el rate limit.
        
        Args:
            identificador: Identificador único (IP, usuario, etc.)
            limite: Número máximo de solicitudes
            ventana_segundos: Ventana de tiempo en segundos
        
        Returns:
            bool: True si está dentro del límite
        """
        ahora = datetime.now()
        
        if identificador not in self._rate_limits:
            self._rate_limits[identificador] = []
        
        # Eliminar solicitudes fuera de la ventana
        self._rate_limits[identificador] = [
            timestamp for timestamp in self._rate_limits[identificador]
            if ahora - timestamp < timedelta(seconds=ventana_segundos)
        ]
        
        # Verificar límite
        if len(self._rate_limits[identificador]) >= limite:
            return False
        
        # Agregar solicitud actual
        self._rate_limits[identificador].append(ahora)
        
        return True
    
    def generar_csrf_token(self) -> str:
        """
        Genera un token CSRF.
        
        Returns:
            str: Token CSRF
        """
        return secrets.token_hex(32)
    
    def validar_csrf_token(self, token: str, token_esperado: str) -> bool:
        """
        Valida un token CSRF.
        
        Args:
            token: Token a validar
            token_esperado: Token esperado
        
        Returns:
            bool: True si el token es válido
        """
        return secrets.compare_digest(token, token_esperado)
    
    def hashear_contrasena(self, password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        Args:
            password: Contraseña en texto plano
        
        Returns:
            str: Contraseña hasheada
        """
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verificar_contrasena(self, password: str, hashed: str) -> bool:
        """
        Verifica una contraseña contra su hash.
        
        Args:
            password: Contraseña en texto plano
            hashed: Contraseña hasheada
        
        Returns:
            bool: True si la contraseña es correcta
        """
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


# Instancia global del gestor de seguridad
security_manager = SecurityManager()


def rate_limit(limite: int = 100, ventana_segundos: int = 60):
    """
    Decorador para aplicar rate limiting a una función.
    
    Args:
        limite: Número máximo de solicitudes
        ventana_segundos: Ventana de tiempo en segundos
    
    Returns:
        Decorador
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Usar IP del usuario o algún identificador
            identificador = kwargs.get('identificador', 'default')
            
            if not security_manager.verificar_rate_limit(identificador, limite, ventana_segundos):
                raise Exception("Rate limit excedido")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
