import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import bcrypt
import jwt

from auth import AuthService
from db_models import Rol, Paciente, Usuario, Medico

@pytest.fixture
def mock_dao():
    with patch("auth.SaludDAO") as mock:
        yield mock

@pytest.fixture
def mock_app_config():
    with patch("auth.get_app_config") as mock:
        mock.return_value = {"secret_key": "test_secret"}
        yield mock

@pytest.fixture
def mock_email_config():
    with patch("auth.get_email_config") as mock:
        mock.return_value = {
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "smtp_username": "test",
            "smtp_password": "test",
            "from_email": "test@test.com"
        }
        yield mock

@pytest.fixture
def auth_service(mock_dao, mock_app_config, mock_email_config):
    return AuthService()

def test_registrar_paciente_exito(auth_service):
    # Arrange
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.obtener_paciente_por_dni.return_value = None
    auth_service.dao.crear_paciente.return_value = "paciente_123"
    auth_service.dao.registrar_usuario.return_value = "usuario_123"

    # Act
    resultado = auth_service.registrar_paciente(
        email="test@test.com",
        password="password",
        nombre="Test User",
        dni="12345678"
    )

    # Assert
    assert resultado == "usuario_123"
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@test.com")
    auth_service.dao.obtener_paciente_por_dni.assert_called_once_with("12345678")
    auth_service.dao.crear_paciente.assert_called_once()
    auth_service.dao.registrar_usuario.assert_called_once()

def test_registrar_paciente_email_existente(auth_service):
    # Arrange
    auth_service.dao.obtener_usuario_por_email.return_value = {"email": "test@test.com"}

    # Act & Assert
    with pytest.raises(ValueError, match="El email ya está registrado"):
        auth_service.registrar_paciente(
            email="test@test.com",
            password="password",
            nombre="Test User",
            dni="12345678"
        )
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@test.com")
    auth_service.dao.crear_paciente.assert_not_called()

def test_registrar_paciente_dni_existente(auth_service):
    # Arrange
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.obtener_paciente_por_dni.return_value = {"dni": "12345678"}

    # Act & Assert
    with pytest.raises(ValueError, match="El DNI ya está registrado"):
        auth_service.registrar_paciente(
            email="test@test.com",
            password="password",
            nombre="Test User",
            dni="12345678"
        )
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@test.com")
    auth_service.dao.obtener_paciente_por_dni.assert_called_once_with("12345678")
    auth_service.dao.crear_paciente.assert_not_called()

def test_login_exito(auth_service):
    # Arrange
    password = "password123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user_123",
        "email": "test@test.com",
        "password_hash": hashed,
        "rol": Rol.PACIENTE,
        "activo": True
    }

    # Act
    token = auth_service.login("test@test.com", password)

    # Assert
    assert token is not None
    assert isinstance(token, str)

def test_login_fallo_password(auth_service):
    # Arrange
    password = "password123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user_123",
        "email": "test@test.com",
        "password_hash": hashed,
        "rol": Rol.PACIENTE,
        "activo": True
    }

    # Act
    token = auth_service.login("test@test.com", "wrongpassword")

    # Assert
    assert token is None

def test_login_fallo_usuario_inactivo(auth_service):
    # Arrange
    password = "password123"
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user_123",
        "email": "test@test.com",
        "password_hash": hashed,
        "rol": Rol.PACIENTE,
        "activo": False
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Usuario desactivado"):
        auth_service.login("test@test.com", password)

def test_verificar_jwt_y_obtener_usuario(auth_service):
    # Arrange
    token = auth_service._generate_jwt_token("user_123", "test@test.com", Rol.PACIENTE)
    auth_service.dao.obtener_usuario_por_id.return_value = {
        "_id": "user_123",
        "email": "test@test.com",
        "nombre": "Test User",
        "rol": Rol.PACIENTE,
        "verificado": True,
        "paciente_id": "pac_123"
    }

    # Act
    usuario_info = auth_service.obtener_usuario_desde_token(token)

    # Assert
    assert usuario_info is not None
    assert usuario_info["id"] == "user_123"
    assert usuario_info["email"] == "test@test.com"
    assert usuario_info["nombre"] == "Test User"
    assert usuario_info["rol"] == Rol.PACIENTE
    assert usuario_info["verificado"] is True

def test_registrar_admin(auth_service):
    # Arrange
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.registrar_usuario.return_value = "admin_123"

    # Act
    resultado = auth_service.registrar_admin(
        email="admin@test.com",
        password="password",
        nombre="Admin User"
    )

    # Assert
    assert resultado == "admin_123"
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("admin@test.com")
    auth_service.dao.registrar_usuario.assert_called_once()

def test_registrar_medico(auth_service):
    # Arrange
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.crear_medico.return_value = "medico_123"
    auth_service.dao.registrar_usuario.return_value = "user_123"

    # Act
    resultado = auth_service.registrar_medico(
        email="medico@test.com",
        password="password",
        nombre="Medico User",
        matricula="12345",
        especialidad_id="esp_1",
        centro_id="centro_1"
    )

    # Assert
    assert resultado == "user_123"
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("medico@test.com")
    auth_service.dao.crear_medico.assert_called_once()
    auth_service.dao.registrar_usuario.assert_called_once()
