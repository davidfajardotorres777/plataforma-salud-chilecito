import pytest
from unittest.mock import patch, MagicMock
from auth import AuthService
from db_models import Rol

@pytest.fixture
def auth_service():
    with patch('auth.SaludDAO') as MockDAO:
        mock_dao = MockDAO.return_value
        service = AuthService()
        service.dao = mock_dao
        yield service

def test_hash_and_verify_password(auth_service):
    password = "mysecretpassword"
    hashed = auth_service._hash_password(password)
    assert hashed != password
    assert auth_service._verify_password(password, hashed) is True
    assert auth_service._verify_password("wrongpassword", hashed) is False

def test_jwt_token_generation_and_verification(auth_service):
    auth_service.app_config["secret_key"] = "testsecret"

    token = auth_service._generate_jwt_token("user_123", "test@test.com", Rol.PACIENTE)

    payload = auth_service._verify_jwt_token(token)
    assert payload is not None
    assert payload["usuario_id"] == "user_123"
    assert payload["email"] == "test@test.com"
    assert payload["rol"] == Rol.PACIENTE

def test_jwt_token_expired(auth_service):
    payload = auth_service._verify_jwt_token("invalid_token")
    assert payload is None

def test_registrar_paciente_success(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.obtener_paciente_por_dni.return_value = None
    auth_service.dao.crear_paciente.return_value = "paciente_123"
    auth_service.dao.registrar_usuario.return_value = "user_123"

    user_id = auth_service.registrar_paciente(
        email="test@example.com",
        password="password123",
        nombre="Test User",
        dni="12345678"
    )

    assert user_id == "user_123"
    auth_service.dao.crear_paciente.assert_called_once()
    auth_service.dao.registrar_usuario.assert_called_once()

def test_registrar_paciente_email_exists(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = {"_id": "existing"}

    with pytest.raises(ValueError, match="El email ya está registrado"):
        auth_service.registrar_paciente(
            email="test@example.com",
            password="password123",
            nombre="Test User",
            dni="12345678"
        )

def test_registrar_paciente_dni_exists(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.obtener_paciente_por_dni.return_value = {"_id": "existing_paciente"}

    with pytest.raises(ValueError, match="El DNI ya está registrado"):
        auth_service.registrar_paciente(
            email="test@example.com",
            password="password123",
            nombre="Test User",
            dni="12345678"
        )

def test_registrar_admin_success(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.registrar_usuario.return_value = "admin_123"

    user_id = auth_service.registrar_admin(
        email="admin@example.com",
        password="password123",
        nombre="Admin User",
        centro_id="centro_1"
    )

    assert user_id == "admin_123"
    auth_service.dao.registrar_usuario.assert_called_once()

def test_registrar_medico_success(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.crear_medico.return_value = "medico_123"
    auth_service.dao.registrar_usuario.return_value = "user_medico_123"

    user_id = auth_service.registrar_medico(
        email="medico@example.com",
        password="password123",
        nombre="Medico User",
        matricula="MP12345",
        especialidad_id="esp_1",
        centro_id="centro_1"
    )

    assert user_id == "user_medico_123"
    auth_service.dao.crear_medico.assert_called_once()
    auth_service.dao.registrar_usuario.assert_called_once()

def test_login_success(auth_service):
    password = "mypassword"
    hashed = auth_service._hash_password(password)
    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user_123",
        "email": "test@example.com",
        "password_hash": hashed,
        "rol": Rol.PACIENTE,
        "activo": True
    }

    auth_service.app_config["secret_key"] = "testsecret"

    token = auth_service.login("test@example.com", password)

    assert token is not None
    payload = auth_service._verify_jwt_token(token)
    assert payload["usuario_id"] == "user_123"

def test_login_failure_conditions(auth_service):
    password = "mypassword"
    hashed = auth_service._hash_password(password)

    # Non-existent user
    auth_service.dao.obtener_usuario_por_email.return_value = None
    assert auth_service.login("test@example.com", "mypassword") is None

    # Wrong password
    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user_123",
        "password_hash": hashed,
        "activo": True
    }
    assert auth_service.login("test@example.com", "wrongpassword") is None

    # Inactive user
    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user_123",
        "password_hash": hashed,
        "activo": False
    }
    with pytest.raises(ValueError, match="Usuario desactivado"):
        auth_service.login("test@example.com", "mypassword")

def test_obtener_usuario_desde_token_success(auth_service):
    auth_service.app_config["secret_key"] = "testsecret"
    token = auth_service._generate_jwt_token("user_123", "test@example.com", Rol.PACIENTE)

    auth_service.dao.obtener_usuario_por_id.return_value = {
        "_id": "user_123",
        "email": "test@example.com",
        "nombre": "Test User",
        "rol": Rol.PACIENTE,
        "verificado": True,
        "paciente_id": "paciente_123"
    }

    usuario = auth_service.obtener_usuario_desde_token(token)

    assert usuario is not None
    assert usuario["id"] == "user_123"
    assert usuario["email"] == "test@example.com"
    assert usuario["nombre"] == "Test User"

def test_obtener_usuario_desde_token_invalid(auth_service):
    assert auth_service.obtener_usuario_desde_token("invalid_token") is None

    auth_service.app_config["secret_key"] = "testsecret"
    token = auth_service._generate_jwt_token("user_123", "test@example.com", Rol.PACIENTE)

    auth_service.dao.obtener_usuario_por_id.return_value = None
    assert auth_service.obtener_usuario_desde_token(token) is None

def test_verificar_email(auth_service):
    auth_service.dao.verificar_email.return_value = True
    assert auth_service.verificar_email("valid_token") is True
    auth_service.dao.verificar_email.assert_called_once_with("valid_token")
