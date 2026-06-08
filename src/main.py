from src.config import OracleDatabase
from src.dao import CentroDAO, MedicoDAO, TurnoDAO


def main() -> None:
    """
    Intenta usar Oracle si está disponible; si no, cae en el store JSON de demo.
    Esto facilita ejecutar `python -m src.main` en entornos donde Oracle no está levantado.
    """
    use_oracle = True
    try:
        db = OracleDatabase()
        try:
            print(f"Conexion Oracle: {db.ping()}")
        except Exception as exc:  # pragma: no cover - depende de entorno local
            print(f"Oracle no disponible: {exc}")
            use_oracle = False
    except Exception as exc:  # pragma: no cover - depende de entorno local
        print(f"Error inicializando OracleDatabase: {exc}")
        use_oracle = False

    if use_oracle:
        centros = CentroDAO(db).listar()
        print(f"Centros cargados: {len(centros)}")

        medicos_cardio = MedicoDAO(db).buscar_por_especialidad("Cardiologia")
        print(f"Medicos de cardiologia: {len(medicos_cardio)}")

        proximos = TurnoDAO(db).listar_proximos(limite=5)
        print("Proximos turnos:")
        for turno in proximos:
            fecha = turno.get("fecha_turno") or turno.get("fecha")
            paciente = turno.get("paciente") or turno.get("paciente_nombre") or turno.get("paciente_id")
            medico = turno.get("medico") or turno.get("medico_nombre") or turno.get("medico_id")
            print(f"- {fecha} | {paciente} | {medico}")
    else:
        # Fallback local demo: usa JsonStore para mostrar información similar sin Oracle.
        print("Usando store JSON de demo (sin Oracle).")
        from src.webapp.store import JsonStore

        store = JsonStore()
        dashboard = store.dashboard()
        print(f"Centros cargados: {len(dashboard.get('centros', []))}")
        # buscar medicos de cardiologia por nombre de especialidad
        especialidades = [e for e in dashboard.get("especialidades", []) if "cardio" in e.get("nombre", "").lower()]
        esp_ids = {int(e["id"]) for e in especialidades}
        medicos = dashboard.get("medicos", [])
        medicos_cardio = [m for m in medicos if int(m.get("especialidad_id", -1)) in esp_ids]
        print(f"Medicos de cardiologia: {len(medicos_cardio)}")

        proximos = sorted(dashboard.get("turnos", []), key=lambda t: t.get("fecha", ""))[:5]
        print("Proximos turnos:")
        for turno in proximos:
            fecha = turno.get("fecha") or turno.get("fecha_turno")
            paciente = (turno.get("paciente") or {}).get("nombre") if isinstance(turno.get("paciente"), dict) else turno.get("paciente")
            medico = (turno.get("medico") or {}).get("nombre") if isinstance(turno.get("medico"), dict) else turno.get("medico")
            print(f"- {fecha} | {paciente} | {medico}")


if __name__ == "__main__":
    main()
