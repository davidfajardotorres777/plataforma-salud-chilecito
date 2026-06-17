"""
Módulo de autenticación para Plataforma Salud Chilecito
=======================================================
Proporciona funcionalidad de registro, login y verificación de usuarios.

Características:
- Registro de pacientes con verificación de email
- Hashing de contraseñas con bcrypt
- Generación y validación de tokens JWT
- Gestión de sesiones con Redis
- Diferenciación de roles (paciente, admin, médico)

Uso básico:
    from auth import AuthService
    from db_models import Usuario, Rol
    
    auth = AuthService()
    
    # Registrar paciente
    usuario_id = auth.registrar_paciente(
        email="juan@example.com",
        password="password123",
        nombre="Juan Pérez",
        dni="12345678"
    )
    
    # Verificar email
    if auth.verificar_email(token):
        print("Email verificado exitosamente")
    
    # Login
    if auth.login("juan@example.com", "password123"):
        print("Login exitoso")
    
    auth.cerrar()
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt

from config_vars import get_app_config, get_email_config
from dao_mongodb import SaludDAO
from db_models import Usuario, Rol, Paciente


class AuthService:
    """
    Servicio de autenticación para la plataforma.
    
    Proporciona métodos para registrar usuarios, verificar emails,
    autenticar sesiones y gestionar tokens JWT.
    """
    
    def __init__(self):
        """
        Inicializa una nueva instancia del servicio de autenticación.
        """
        self.dao = SaludDAO()
        self.app_config = get_app_config()
        self.email_config = get_email_config()
    
    def _hash_password(self, password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        Args:
            password: Contraseña en texto plano
        
        Returns:
            str: Contraseña hasheada
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """
        Verifica una contraseña contra su hash.
        
        Args:
            password: Contraseña en texto plano
            hashed: Contraseña hasheada
        
        Returns:
            bool: True si la contraseña es correcta
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def _generate_jwt_token(self, usuario_id: str, email: str, rol: str) -> str:
        """
        Genera un token JWT para autenticación.
        
        Args:
            usuario_id: ID del usuario
            email: Email del usuario
            rol: Rol del usuario
        
        Returns:
            str: Token JWT
        """
        secret = self.app_config["secret_key"]
        payload = {
            "usuario_id": usuario_id,
            "email": email,
            "rol": rol,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, secret, algorithm="HS256")
    
    def _verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica un token JWT.
        
        Args:
            token: Token JWT
        
        Returns:
            dict | None: Payload del token si es válido
        """
        try:
            secret = self.app_config["secret_key"]
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def registrar_paciente(
        self,
        email: str,
        password: str,
        nombre: str,
        dni: str,
        telefono: Optional[str] = None,
        distrito: Optional[str] = None,
        obra_social: Optional[str] = None
    ) -> str:
        """
        Registra un nuevo paciente con su cuenta de usuario.
        
        Args:
            email: Email del paciente
            password: Contraseña del paciente
            nombre: Nombre completo del paciente
            dni: DNI del paciente
            telefono: Teléfono del paciente (opcional)
            distrito: Distrito del paciente (opcional)
            obra_social: Obra social del paciente (opcional)
        
        Returns:
            str: ID del usuario creado
        """
        # Verificar si el email ya existe
        if self.dao.obtener_usuario_por_email(email):
            raise ValueError("El email ya está registrado")
        
        # Verificar si el DNI ya existe
        if self.dao.obtener_paciente_por_dni(dni):
            raise ValueError("El DNI ya está registrado")
        
        # Crear paciente
        paciente = Paciente(
            dni=dni,
            nombre=nombre,
            telefono=telefono,
            distrito=distrito,
            obra_social=obra_social,
            email=email
        )
        paciente_id = self.dao.crear_paciente(paciente)
        
        # Crear usuario (verificado automáticamente)
        password_hash = self._hash_password(password)
        usuario = Usuario(
            email=email,
            password_hash=password_hash,
            rol=Rol.PACIENTE,
            nombre=nombre,
            paciente_id=paciente_id,
            verificado=True,  # Verificado automáticamente
            fecha_registro=datetime.now()
        )
        usuario_id = self.dao.registrar_usuario(usuario)
        
        return usuario_id
    
    def _enviar_email_verificacion(self, email: str, token: str) -> bool:
        """
        Envía un email de verificación al usuario.
        
        Args:
            email: Email del destinatario
            token: Token de verificación
        
        Returns:
            bool: True si el email se envió exitosamente
        """
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        try:
            # Verificar configuración de email
            if not self.email_config.get("smtp_username") or not self.email_config.get("smtp_password"):
                print(f"⚠️ Configuración de email incompleta. No se puede enviar email a {email}")
                return False
            
            # Crear enlace de verificación
            base_url = self.app_config.get("base_url", "http://localhost:8000")
            verification_url = f"{base_url}/verificar-email?token={token}"
            
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Verifica tu email - Salud Chilecito'
            msg['From'] = self.email_config["from_email"]
            msg['To'] = email
            
            # Cuerpo del email
            html = f"""
            <html>
            <body>
                <h2>Bienvenido a Salud Chilecito</h2>
                <p>Gracias por registrarte en nuestra plataforma.</p>
                <p>Para verificar tu email, haz clic en el siguiente enlace:</p>
                <p><a href="{verification_url}">Verificar Email</a></p>
                <p>Este enlace expirará en 24 horas.</p>
                <p>Si no solicitaste este registro, por favor ignora este email.</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Enviar email
            with smtplib.SMTP(
                self.email_config["smtp_server"],
                self.email_config["smtp_port"]
            ) as server:
                server.starttls()
                server.login(
                    self.email_config["smtp_username"],
                    self.email_config["smtp_password"]
                )
                server.send_message(msg)
            
            print(f"✅ Email de verificación enviado a {email}")
            return True
        except Exception as e:
            print(f"❌ Error al enviar email de verificación: {e}")
            return False
    
    def registrar_admin(
        self,
        email: str,
        password: str,
        nombre: str,
        centro_id: Optional[str] = None
    ) -> str:
        """
        Registra un nuevo administrador del sistema.
        
        Args:
            email: Email del administrador
            password: Contraseña del administrador
            nombre: Nombre completo del administrador
            centro_id: ID del centro (opcional)
        
        Returns:
            str: ID del usuario creado
        """
        # Verificar si el email ya existe
        if self.dao.obtener_usuario_por_email(email):
            raise ValueError("El email ya está registrado")
        
        # Crear usuario (verificado automáticamente)
        password_hash = self._hash_password(password)
        usuario = Usuario(
            email=email,
            password_hash=password_hash,
            rol=Rol.ADMIN,
            nombre=nombre,
            centro_id=centro_id,
            verificado=True,  # Verificado automáticamente
            fecha_registro=datetime.now()
        )
        usuario_id = self.dao.registrar_usuario(usuario)
        
        return usuario_id
    
    def registrar_medico(
        self,
        email: str,
        password: str,
        nombre: str,
        matricula: str,
        especialidad_id: str,
        centro_id: str,
        telefono: Optional[str] = None
    ) -> str:
        """
        Registra un nuevo médico del sistema.
        
        Args:
            email: Email del médico
            password: Contraseña del médico
            nombre: Nombre completo del médico
            matricula: Matrícula del médico
            especialidad_id: ID de la especialidad
            centro_id: ID del centro
            telefono: Teléfono del médico (opcional)
        
        Returns:
            str: ID del usuario creado
        """
        # Verificar si el email ya existe
        if self.dao.obtener_usuario_por_email(email):
            raise ValueError("El email ya está registrado")
        
        # Crear médico
        from db_models import Medico
        medico = Medico(
            nombre=nombre,
            matricula=matricula,
            especialidad_id=especialidad_id,
            centro_id=centro_id,
            telefono=telefono,
            email=email
        )
        medico_id = self.dao.crear_medico(medico)
        
        # Crear usuario (verificado automáticamente)
        password_hash = self._hash_password(password)
        usuario = Usuario(
            email=email,
            password_hash=password_hash,
            rol=Rol.MEDICO,
            nombre=nombre,
            medico_id=medico_id,
            centro_id=centro_id,
            verificado=True,  # Verificado automáticamente
            fecha_registro=datetime.now()
        )
        usuario_id = self.dao.registrar_usuario(usuario)
        
        return usuario_id
    
    def verificar_email(self, token: str) -> bool:
        """
        Verifica el email de un usuario usando el token.
        
        Args:
            token: Token de verificación
        
        Returns:
            bool: True si la verificación fue exitosa
        """
        return self.dao.verificar_email(token)
    
    def login(self, email: str, password: str) -> Optional[str]:
        """
        Autentica un usuario y genera un token JWT.
        
        Args:
            email: Email del usuario
            password: Contraseña del usuario
        
        Returns:
            str | None: Token JWT si la autenticación es exitosa
        """
        # Obtener usuario
        usuario = self.dao.obtener_usuario_por_email(email)
        if not usuario:
            return None
        
        # Verificar contraseña
        if not self._verify_password(password, usuario["password_hash"]):
            return None
        
        # Verificar si el usuario está activo y verificado
        if not usuario.get("activo", False):
            raise ValueError("Usuario desactivado")
        
        if not usuario.get("verificado", False):
            raise ValueError("Email no verificado")
        
        # Generar token JWT
        token = self._generate_jwt_token(
            str(usuario["_id"]),
            usuario["email"],
            usuario["rol"]
        )
        
        return token
    
    def obtener_usuario_desde_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del usuario desde un token JWT.
        
        Args:
            token: Token JWT
        
        Returns:
            dict | None: Información del usuario si el token es válido
        """
        payload = self._verify_jwt_token(token)
        if not payload:
            return None
        
        usuario = self.dao.obtener_usuario_por_id(payload["usuario_id"])
        if not usuario:
            return None
        
        return {
            "id": str(usuario["_id"]),
            "email": usuario["email"],
            "nombre": usuario["nombre"],
            "rol": usuario["rol"],
            "verificado": usuario.get("verificado", False),
            "paciente_id": usuario.get("paciente_id"),
            "medico_id": usuario.get("medico_id"),
        }
    
    def cerrar(self):
        """Cierra la conexión con la base de datos."""
        self.dao.cerrar()
