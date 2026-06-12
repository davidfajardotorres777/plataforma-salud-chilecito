"""
Seed para MongoDB - Plataforma Salud Chilecito
================================================
Carga datos iniciales en MongoDB para la plataforma.

Uso:
    python seed_mongodb.py
"""

from datetime import datetime
from dao_mongodb import SaludDAO
from db_models import CentroSalud, Especialidad, Medico, Paciente, Usuario, Rol


def seed_centros(dao: SaludDAO) -> None:
    """Carga centros de salud iniciales."""
    centros = [
        CentroSalud(
            nombre="Hospital Regional Chilecito",
            direccion="Av. Libertador 123",
            distrito="Chilecito",
            tipo="HOSPITAL",
            telefono="3825-420000",
            email="contacto@hospitalchilecito.com"
        ),
        CentroSalud(
            nombre="Centro de Salud Nonogasta",
            direccion="Calle San Martín 456",
            distrito="Nonogasta",
            tipo="CENTRO_SALUD",
            telefono="3825-430000"
        ),
        CentroSalud(
            nombre="Clínica Santa María",
            direccion="Av. San Martín 789",
            distrito="Chilecito",
            tipo="CLINICA",
            telefono="3825-440000",
            email="info@clinicasantamaria.com"
        )
    ]
    
    for centro in centros:
        try:
            centro_id = dao.crear_centro(centro)
            print(f"Centro creado: {centro.nombre} (ID: {centro_id})")
        except Exception as e:
            print(f"Error al crear centro {centro.nombre}: {e}")


def seed_especialidades(dao: SaludDAO) -> None:
    """Carga especialidades médicas iniciales."""
    especialidades = [
        Especialidad(
            nombre="Cardiología",
            descripcion="Especialidad médica que se encarga del diagnóstico y tratamiento de las enfermedades del corazón"
        ),
        Especialidad(
            nombre="Medicina General",
            descripcion="Especialidad médica que aborda el cuidado general de la salud"
        ),
        Especialidad(
            nombre="Pediatría",
            descripcion="Especialidad médica que se ocupa de la salud de los niños"
        ),
        Especialidad(
            nombre="Traumatología",
            descripcion="Especialidad médica que trata lesiones del sistema musculoesquelético"
        ),
        Especialidad(
            nombre="Ginecología",
            descripcion="Especialidad médica que se ocupa de la salud de la mujer"
        )
    ]
    
    for esp in especialidades:
        try:
            esp_id = dao.crear_especialidad(esp)
            print(f"Especialidad creada: {esp.nombre} (ID: {esp_id})")
        except Exception as e:
            print(f"Error al crear especialidad {esp.nombre}: {e}")


def seed_medicos(dao: SaludDAO) -> None:
    """Carga médicos iniciales."""
    # Primero obtenemos centros y especialidades
    centros = dao.listar_centros()
    especialidades = dao.listar_especialidades()
    
    if not centros or not especialidades:
        print("Error: No hay centros o especialidades. Ejecuta seed_centros y seed_especialidades primero.")
        return
    
    # Obtener el primer centro y especialidad
    centro = centros[0]
    especialidad = especialidades[0]
    
    # Los IDs de MongoDB vienen como strings en el diccionario
    centro_id = centro.get("_id")
    especialidad_id = especialidad.get("_id")
    
    if not centro_id or not especialidad_id:
        print("Error: No se pudieron obtener IDs de centro o especialidad.")
        print(f"Centro: {centro}")
        print(f"Especialidad: {especialidad}")
        return
    
    medicos = [
        Medico(
            nombre="Dr. Juan Pérez",
            matricula="12345",
            especialidad_id=str(centro_id),
            centro_id=str(especialidad_id),
            telefono="3825-123456",
            email="juan.perez@hospital.com"
        ),
        Medico(
            nombre="Dra. María González",
            matricula="12346",
            especialidad_id=str(centro_id),
            centro_id=str(especialidad_id),
            telefono="3825-123457",
            email="maria.gonzalez@hospital.com"
        )
    ]
    
    for medico in medicos:
        try:
            medico_id = dao.crear_medico(medico)
            print(f"Médico creado: {medico.nombre} (ID: {medico_id})")
        except Exception as e:
            print(f"Error al crear médico {medico.nombre}: {e}")


def seed_admin_usuario(dao: SaludDAO) -> None:
    """Crea un usuario administrador inicial."""
    try:
        # Verificar si ya existe un admin
        admin_existente = dao.obtener_usuario_por_email("admin@saludchilecito.com")
        if admin_existente:
            print("Usuario admin ya existe. Saltando creación.")
            return
        
        # Crear usuario admin
        import bcrypt
        password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        admin = Usuario(
            email="admin@saludchilecito.com",
            password_hash=password_hash,
            rol=Rol.ADMIN,
            nombre="Administrador",
            verificado=True,
            fecha_registro=datetime.now()
        )
        
        usuario_id = dao.registrar_usuario(admin)
        print(f"Usuario admin creado: {admin.email} (ID: {usuario_id})")
        print("Contraseña: admin123")
    except Exception as e:
        print(f"Error al crear usuario admin: {e}")


def main():
    """Función principal que ejecuta todos los seeds."""
    print("=== Seed para MongoDB - Plataforma Salud Chilecito ===\n")
    
    dao = SaludDAO()
    
    # Verificar conexión
    status = dao.ping()
    print(f"Estado de conexión MongoDB: {status}")
    
    if status != "OK":
        print("Error: No se puede conectar a MongoDB. Asegúrate de que MongoDB esté corriendo.")
        return
    
    print("\nCargando datos iniciales...\n")
    
    # Cargar datos
    seed_centros(dao)
    print()
    seed_especialidades(dao)
    print()
    seed_medicos(dao)
    print()
    seed_admin_usuario(dao)
    
    print("\n=== Seed completado ===")
    print(f"\nTotales:")
    print(f"  Centros: {dao.contar('centros')}")
    print(f"  Especialidades: {dao.contar('especialidades')}")
    print(f"  Médicos: {dao.contar('medicos')}")
    print(f"  Pacientes: {dao.contar('pacientes')}")
    print(f"  Usuarios: {dao.contar('usuarios')}")
    
    dao.cerrar()


if __name__ == "__main__":
    main()
