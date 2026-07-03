import pytest
from unittest.mock import MagicMock
from auth import AuthService

class TestAuth:
    """Tests for the auth module"""

    def test_login_inactive_user(self):
        """Test login with an inactive user raises ValueError"""
        auth_service = AuthService()

        # Mocking the dao to return an inactive user
        auth_service.dao = MagicMock()
        auth_service.dao.obtener_usuario_por_email.return_value = {
            "_id": "some_id",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "activo": False,
            "rol": "paciente"
        }

        # Mocking password verification to pass
        auth_service._verify_password = MagicMock(return_value=True)

        # Asserting that ValueError is raised
        with pytest.raises(ValueError, match="Usuario desactivado"):
            auth_service.login("test@example.com", "password123")
