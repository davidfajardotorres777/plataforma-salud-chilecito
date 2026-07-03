import pytest
from unittest.mock import MagicMock
from auth import AuthService

class TestAuthLogin:
    @pytest.fixture
    def auth_service(self):
        auth = AuthService()
        auth.dao = MagicMock()
        auth._verify_password = MagicMock()
        auth._generate_jwt_token = MagicMock()
        # Mock para evitar que el __init__ original falle por configuraciones faltantes si las hubiera
        # Aunque aquí __init__ de AuthService ya se ejecutó, podemos sobrescribir dependencias
        return auth

    def test_login_success(self, auth_service):
        # Configurar mocks
        mock_user = {
            "_id": "user_123",
            "email": "test@example.com",
            "password_hash": "hashed_pass",
            "activo": True,
            "rol": "paciente"
        }
        auth_service.dao.obtener_usuario_por_email.return_value = mock_user
        auth_service._verify_password.return_value = True
        auth_service._generate_jwt_token.return_value = "fake_jwt_token"

        # Ejecutar método
        token = auth_service.login("test@example.com", "password123")

        # Verificaciones
        assert token == "fake_jwt_token"
        auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
        auth_service._verify_password.assert_called_once_with("password123", "hashed_pass")
        auth_service._generate_jwt_token.assert_called_once_with("user_123", "test@example.com", "paciente")

    def test_login_user_not_found(self, auth_service):
        # Configurar mocks
        auth_service.dao.obtener_usuario_por_email.return_value = None

        # Ejecutar método
        token = auth_service.login("unknown@example.com", "password123")

        # Verificaciones
        assert token is None
        auth_service.dao.obtener_usuario_por_email.assert_called_once_with("unknown@example.com")
        auth_service._verify_password.assert_not_called()
        auth_service._generate_jwt_token.assert_not_called()

    def test_login_invalid_password(self, auth_service):
        # Configurar mocks
        mock_user = {
            "_id": "user_123",
            "email": "test@example.com",
            "password_hash": "hashed_pass",
            "activo": True,
            "rol": "paciente"
        }
        auth_service.dao.obtener_usuario_por_email.return_value = mock_user
        auth_service._verify_password.return_value = False

        # Ejecutar método
        token = auth_service.login("test@example.com", "wrong_password")

        # Verificaciones
        assert token is None
        auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
        auth_service._verify_password.assert_called_once_with("wrong_password", "hashed_pass")
        auth_service._generate_jwt_token.assert_not_called()

    def test_login_inactive_user(self, auth_service):
        # Configurar mocks
        mock_user = {
            "_id": "user_123",
            "email": "test@example.com",
            "password_hash": "hashed_pass",
            "activo": False, # Usuario inactivo
            "rol": "paciente"
        }
        auth_service.dao.obtener_usuario_por_email.return_value = mock_user
        auth_service._verify_password.return_value = True

        # Ejecutar método y verificar excepción
        with pytest.raises(ValueError) as excinfo:
            auth_service.login("test@example.com", "password123")

        # Verificaciones
        assert str(excinfo.value) == "Usuario desactivado"
        auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
        auth_service._verify_password.assert_called_once_with("password123", "hashed_pass")
        auth_service._generate_jwt_token.assert_not_called()
