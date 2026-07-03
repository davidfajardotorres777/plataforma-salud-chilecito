import pytest
from unittest.mock import MagicMock
from auth import AuthService
from db_models import Usuario, Rol, Paciente

@pytest.fixture
def auth_service():
    """Fixture para crear una instancia de AuthService con DAO mockeado."""
    auth = AuthService()
    auth.dao = MagicMock()
    # Mockear el método _hash_password para simplificar
    auth._hash_password = MagicMock(return_value="hashed_password")
    return auth

def test_registrar_paciente_exito(auth_service):
    """Test de registro de paciente exitoso (Happy path)."""
    # Configurar los mocks
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.obtener_paciente_por_dni.return_value = None
    auth_service.dao.crear_paciente.return_value = "paciente_123"
    auth_service.dao.registrar_usuario.return_value = "usuario_456"

    # Llamar al método
    usuario_id = auth_service.registrar_paciente(
        email="test@example.com",
        password="securepassword",
        nombre="Juan Perez",
        dni="12345678",
        telefono="555-1234",
        distrito="Centro",
        obra_social="OSDE"
    )

    # Verificaciones
    assert usuario_id == "usuario_456"

    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
    auth_service.dao.obtener_paciente_por_dni.assert_called_once_with("12345678")


    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
    auth_service.dao.obtener_paciente_por_dni.assert_called_once_with("12345678")

    # Verificar que crear_paciente se llamó con un objeto Paciente correcto
    auth_service.dao.crear_paciente.assert_called_once()
    args, _ = auth_service.dao.crear_paciente.call_args
    paciente_creado = args[0]
    assert isinstance(paciente_creado, Paciente)
    assert paciente_creado.email == "test@example.com"
    assert paciente_creado.dni == "12345678"
    assert paciente_creado.nombre == "Juan Perez"
    assert paciente_creado.telefono == "555-1234"
    assert paciente_creado.distrito == "Centro"
    assert paciente_creado.obra_social == "OSDE"

    # Verificar hash de password
    auth_service._hash_password.assert_called_once_with("securepassword")

    # Verificar que registrar_usuario se llamó con un objeto Usuario correcto
    auth_service.dao.registrar_usuario.assert_called_once()
    args, _ = auth_service.dao.registrar_usuario.call_args
    usuario_creado = args[0]
    assert isinstance(usuario_creado, Usuario)
    assert usuario_creado.email == "test@example.com"
    assert usuario_creado.password_hash == "hashed_password"
    assert usuario_creado.rol == Rol.PACIENTE
    assert usuario_creado.nombre == "Juan Perez"
    assert usuario_creado.paciente_id == "paciente_123"
    assert usuario_creado.verificado is True
    assert usuario_creado.fecha_registro is not None


def test_registrar_paciente_email_existente(auth_service):
    """Test para verificar que falla si el email ya existe."""
    # Configurar mock para que devuelva un usuario existente
    auth_service.dao.obtener_usuario_por_email.return_value = {"email": "test@example.com"}

    # Llamar al método y esperar ValueError
    with pytest.raises(ValueError, match="El email ya está registrado"):
        auth_service.registrar_paciente(
            email="test@example.com",
            password="securepassword",
            nombre="Juan Perez",
            dni="12345678"
        )


    # Verificaciones
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
    auth_service.dao.obtener_paciente_por_dni.assert_not_called()
    auth_service.dao.crear_paciente.assert_not_called()
    auth_service.dao.registrar_usuario.assert_not_called()


def test_registrar_paciente_dni_existente(auth_service):
    """Test para verificar que falla si el DNI ya existe."""
    # Configurar mock
    auth_service.dao.obtener_usuario_por_email.return_value = None
    auth_service.dao.obtener_paciente_por_dni.return_value = {"dni": "12345678"}

    # Llamar al método y esperar ValueError
    with pytest.raises(ValueError, match="El DNI ya está registrado"):
        auth_service.registrar_paciente(
            email="test@example.com",
            password="securepassword",
            nombre="Juan Perez",
            dni="12345678"
        )


    # Verificaciones
    auth_service.dao.obtener_usuario_por_email.assert_called_once_with("test@example.com")
    auth_service.dao.obtener_paciente_por_dni.assert_called_once_with("12345678")
    auth_service.dao.crear_paciente.assert_not_called()
    auth_service.dao.registrar_usuario.assert_not_called()
