import pytest
from unittest.mock import MagicMock, patch
from auth import AuthService

@pytest.fixture
def auth_service():
    with patch('auth.SaludDAO'), \
         patch('auth.get_app_config'), \
         patch('auth.get_email_config'):
        service = AuthService()
        yield service

def test_login_success(auth_service):
    # Configurar mocks
    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "password_hash": "hashed_pass",
        "rol": "paciente",
        "activo": True
    }

    with patch.object(auth_service, '_verify_password', return_value=True) as mock_verify, \
         patch.object(auth_service, '_generate_jwt_token', return_value="fake_token") as mock_generate:

        token = auth_service.login("test@example.com", "password")

        assert token == "fake_token"
        mock_verify.assert_called_once_with("password", "hashed_pass")
        mock_generate.assert_called_once_with("user123", "test@example.com", "paciente")
        auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")

def test_login_user_not_found(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = None

    token = auth_service.login("nonexistent@example.com", "password")

    assert token is None
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("nonexistent@example.com")

def test_login_invalid_password(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "password_hash": "hashed_pass",
        "rol": "paciente",
        "activo": True
    }

    with patch.object(auth_service, '_verify_password', return_value=False) as mock_verify:
        token = auth_service.login("test@example.com", "wrong_password")

        assert token is None
        mock_verify.assert_called_once_with("wrong_password", "hashed_pass")

def test_login_user_inactive(auth_service):
    auth_service.dao.obtener_usuario_por_email.return_value = {
        "_id": "user123",
        "email": "test@example.com",
        "password_hash": "hashed_pass",
        "rol": "paciente",
        "activo": False
    }

    with patch.object(auth_service, '_verify_password', return_value=True) as mock_verify:
        with pytest.raises(ValueError, match="Usuario desactivado"):
            auth_service.login("test@example.com", "password")

        mock_verify.assert_called_once_with("password", "hashed_pass")
