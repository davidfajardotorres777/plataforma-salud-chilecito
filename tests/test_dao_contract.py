from datetime import datetime

from src.dao import CentroDAO, EspecialidadDAO, PacienteDAO, TurnoDAO
from src.models import CentroSalud, Especialidad, Paciente, Turno


class FakeDB:
    def __init__(self):
        self.calls = []

    def fetch_all(self, sql, params=None):
        self.calls.append(("fetch_all", " ".join(sql.split()), params or {}))
        return []

    def fetch_one(self, sql, params=None):
        self.calls.append(("fetch_one", " ".join(sql.split()), params or {}))
        return {"total": 0}

    def execute(self, sql, params=None):
        self.calls.append(("execute", " ".join(sql.split()), params or {}))
        return 1


def test_especialidad_dao_creates_insert_with_named_params():
    db = FakeDB()
    dao = EspecialidadDAO(db)

    affected = dao.crear(Especialidad(nombre="Cardiologia", descripcion="Control cardiovascular"))

    assert affected == 1
    kind, sql, params = db.calls[-1]
    assert kind == "execute"
    assert "INSERT INTO especialidad" in sql
    assert params["nombre"] == "Cardiologia"


def test_centro_dao_filters_by_district():
    db = FakeDB()
    dao = CentroDAO(db)

    dao.listar(distrito="Nonogasta")

    kind, sql, params = db.calls[-1]
    assert kind == "fetch_all"
    assert "WHERE UPPER(distrito)" in sql
    assert params == {"distrito": "Nonogasta"}


def test_paciente_contact_update_uses_patient_id():
    db = FakeDB()
    dao = PacienteDAO(db)

    dao.actualizar_contacto(7, "3825-111222", "paciente@mail.com")

    _, sql, params = db.calls[-1]
    assert "UPDATE paciente" in sql
    assert params["id_paciente"] == 7
    assert params["telefono"] == "3825-111222"


def test_turno_reservation_includes_price_and_state():
    db = FakeDB()
    dao = TurnoDAO(db)
    turno = Turno(
        id_paciente=1,
        id_medico=2,
        id_centro=3,
        fecha_turno=datetime(2026, 6, 1, 9, 30),
        estado="CONFIRMADO",
        precio_consulta=12000,
    )

    dao.reservar(turno)

    _, sql, params = db.calls[-1]
    assert "INSERT INTO turno" in sql
    assert params["estado"] == "CONFIRMADO"
    assert params["precio_consulta"] == 12000


def test_model_dataclasses_keep_project_language():
    centro = CentroSalud(
        nombre="Centro de Salud Sanogasta",
        direccion="9 de Julio s/n",
        distrito="Sanogasta",
        tipo="PUBLICO",
    )
    paciente = Paciente(dni="40111222", nombre="Juan Perez")

    assert centro.distrito == "Sanogasta"
    assert paciente.dni == "40111222"
