from src.config import OracleDatabase
from src.dao import CentroDAO, MedicoDAO, TurnoDAO


def main() -> None:
    db = OracleDatabase()
    print(f"Conexion Oracle: {db.ping()}")

    centros = CentroDAO(db).listar()
    print(f"Centros cargados: {len(centros)}")

    medicos_cardio = MedicoDAO(db).buscar_por_especialidad("Cardiologia")
    print(f"Medicos de cardiologia: {len(medicos_cardio)}")

    proximos = TurnoDAO(db).listar_proximos(limite=5)
    print("Proximos turnos:")
    for turno in proximos:
        print(f"- {turno['fecha_turno']} | {turno['paciente']} | {turno['medico']}")


if __name__ == "__main__":
    main()
