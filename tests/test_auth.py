import pytest
from unittest.mock import MagicMock
from auth import AuthService

def test_registrar_paciente_email_existente():
    auth = AuthService()
    auth.dao = MagicMock()
    auth.dao.obtener_usuario_por_email.return_value = {"email": "test@example.com"}

    with pytest.raises(ValueError, match="El email ya está registrado"):
        auth.registrar_paciente(
            email="test@example.com",
            password="password123",
            nombre="Test User",
            dni="12345678"
        )

def test_registrar_paciente_dni_existente():
    auth = AuthService()
    auth.dao = MagicMock()
    auth.dao.obtener_usuario_por_email.return_value = None
    auth.dao.obtener_paciente_por_dni.return_value = {"dni": "12345678"}

    with pytest.raises(ValueError, match="El DNI ya está registrado"):
        auth.registrar_paciente(
            email="test@example.com",
            password="password123",
            nombre="Test User",
            dni="12345678"
        )
