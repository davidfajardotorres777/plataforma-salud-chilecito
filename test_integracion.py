"""
Test de Integración - Plataforma Salud Chilecito
================================================
Verifica que todos los componentes funcionen correctamente.

Uso:
    python test_integracion.py
"""

from dao_mongodb import SaludDAO
from redis_cache import RedisCache
from auth import AuthService
from db_models import CentroSalud, Paciente, Usuario, Rol


def test_mongodb():
    """Prueba la conexión y operaciones básicas de MongoDB."""
    print("=== Prueba de MongoDB ===")
    
    dao = SaludDAO()
    
    # Verificar conexión
    status = dao.ping()
    print(f"Estado de conexión MongoDB: {status}")
    
    if status != "OK":
        print("❌ Error: No se puede conectar a MongoDB")
        return False
    
    # Contar documentos
    centros_count = dao.contar("centros")
    pacientes_count = dao.contar("pacientes")
    usuarios_count = dao.contar("usuarios")
    
    print(f"✅ Centros: {centros_count}")
    print(f"✅ Pacientes: {pacientes_count}")
    print(f"✅ Usuarios: {usuarios_count}")
    
    dao.cerrar()
    return True


def test_redis():
    """Prueba la conexión y operaciones básicas de Redis."""
    print("\n=== Prueba de Redis ===")
    
    cache = RedisCache()
    
    # Verificar conexión
    status = cache.ping()
    print(f"Estado de conexión Redis: {status}")
    
    if status != "OK":
        print("❌ Error: No se puede conectar a Redis")
        return False
    
    # Probar set/get
    test_data = {"test": "data", "timestamp": "2024-01-01"}
    cache.set("test_key", test_data, ttl=60)
    retrieved = cache.get("test_key")
    
    if retrieved == test_data:
        print("✅ Set/Get funciona correctamente")
    else:
        print("❌ Error: Set/Get no funciona")
        return False
    
    # Probar sesión
    session_data = {"usuario_id": "test", "email": "test@example.com"}
    cache.set_session("test_session", session_data, ttl=60)
    session = cache.get_session("test_session")
    
    if session == session_data:
        print("✅ Sesiones funcionan correctamente")
    else:
        print("❌ Error: Sesiones no funcionan")
        return False
    
    # Limpiar
    cache.delete("test_key")
    cache.delete_session("test_session")
    
    cache.cerrar()
    return True


def test_auth():
    """Prueba el servicio de autenticación."""
    print("\n=== Prueba de Autenticación ===")
    
    auth = AuthService()
    
    # Probar hashing de contraseña
    password = "test123"
    hashed = auth._hash_password(password)
    verified = auth._verify_password(password, hashed)
    
    if verified:
        print("✅ Hashing de contraseñas funciona")
    else:
        print("❌ Error: Hashing de contraseñas no funciona")
        return False
    
    # Probar generación de token JWT
    token = auth._generate_jwt_token("test_id", "test@example.com", "paciente")
    
    if token:
        print("✅ Generación de JWT funciona")
    else:
        print("❌ Error: Generación de JWT no funciona")
        return False
    
    # Probar verificación de token JWT
    payload = auth._verify_jwt_token(token)
    
    if payload and payload["email"] == "test@example.com":
        print("✅ Verificación de JWT funciona")
    else:
        print("❌ Error: Verificación de JWT no funciona")
        return False
    
    auth.cerrar()
    return True


def test_dao_operations():
    """Prueba operaciones CRUD del DAO."""
    print("\n=== Prueba de Operaciones DAO ===")
    
    dao = SaludDAO()
    
    # Crear centro de prueba
    centro = CentroSalud(
        nombre="Centro de Prueba",
        direccion="Calle Test 123",
        distrito="Test",
        tipo="CENTRO_SALUD"
    )
    
    try:
        centro_id = dao.crear_centro(centro)
        print(f"✅ Centro creado: {centro_id}")
        
        # Listar centros
        centros = dao.listar_centros()
        print(f"✅ Listar centros: {len(centros)} centros")
        
        # Filtrar por distrito
        centros_test = dao.listar_centros(distrito="Test")
        print(f"✅ Filtrar por distrito: {len(centros_test)} centros")
        
    except Exception as e:
        print(f"❌ Error en operaciones DAO: {e}")
        return False
    
    dao.cerrar()
    return True


def main():
    """Ejecuta todas las pruebas de integración."""
    print("=== TEST DE INTEGRACIÓN - Plataforma Salud Chilecito ===\n")
    
    results = []
    
    # Ejecutar pruebas
    results.append(("MongoDB", test_mongodb()))
    results.append(("Redis", test_redis()))
    results.append(("Autenticación", test_auth()))
    results.append(("DAO Operations", test_dao_operations()))
    
    # Resumen
    print("\n=== RESUMEN ===")
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✅ Todas las pruebas pasaron exitosamente")
    else:
        print("\n❌ Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return all_passed


if __name__ == "__main__":
    main()
