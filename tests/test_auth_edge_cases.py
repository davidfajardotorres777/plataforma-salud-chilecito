import pytest
from unittest.mock import MagicMock
from auth import AuthService

def test_registrar_paciente_dni_existente():
    """Prueba que registrar_paciente lance ValueError cuando el DNI ya existe."""
    auth_service = AuthService()

    # Mockear las funciones del DAO para aislar la prueba
    auth_service.dao = MagicMock()

    # Simular que el correo no existe
    auth_service.dao.obtener_usuario_por_email.return_value = None

    # Simular que el DNI ya existe
    auth_service.dao.obtener_paciente_por_dni.return_value = True

    with pytest.raises(ValueError, match="El DNI ya está registrado"):
        auth_service.registrar_paciente(
            email="nuevo@example.com",
            password="password123",
            nombre="Juan Perez",
            dni="12345678"
        )

    # Verificar que se llamó a obtener_paciente_por_dni con el DNI correcto
    auth_service.dao.obtener_paciente_por_dni.assert_called_once_with("12345678")
