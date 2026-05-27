from datetime import datetime, timedelta

from src.dao import CentroDAO, EspecialidadDAO, MedicoDAO, PacienteDAO, TurnoDAO
from src.models import CentroSalud, Especialidad, Medico, Paciente, Turno


def run_seed() -> None:
    especialidades = EspecialidadDAO()
    centros = CentroDAO()
    medicos = MedicoDAO()
    pacientes = PacienteDAO()
    turnos = TurnoDAO()

    especialidades.crear(Especialidad("Clinica Medica", "Atencion primaria"))
    especialidades.crear(Especialidad("Pediatria", "Atencion de ninos y adolescentes"))

    centros.crear(
        CentroSalud(
            nombre="Hospital Eleazar Herrera Motta",
            direccion="Av. La Mexicana 180",
            distrito="Chilecito",
            tipo="PUBLICO",
            telefono="3825-422100",
        )
    )

    # En un seed real se consultan los IDs generados por Oracle. Estos valores
    # coinciden con una base vacia usando identidades desde 1.
    medicos.crear(
        Medico(
            nombre="Dra. Maria Gonzalez",
            matricula="LR-SEED-001",
            id_especialidad=1,
            id_centro=1,
            telefono="3825-500001",
        )
    )

    pacientes.crear(
        Paciente(
            dni="40111222",
            nombre="Juan Perez",
            telefono="3825-600001",
            obra_social="APOS",
            distrito="Chilecito",
        )
    )

    turnos.reservar(
        Turno(
            id_paciente=1,
            id_medico=1,
            id_centro=1,
            fecha_turno=datetime.now() + timedelta(days=1),
            estado="CONFIRMADO",
            precio_consulta=0,
            observaciones="Turno cargado por seed Python",
        )
    )

    print("Seed Python completado.")


if __name__ == "__main__":
    run_seed()
