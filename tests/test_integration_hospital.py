import json
from tempfile import TemporaryDirectory
from pathlib import Path

from src.webapp.store import JsonStore
from src.webapp.server import filter_dashboard_by_centro, centro_id_for_slug_or_host

ROOT = Path(__file__).resolve().parents[1]


def _make_store(tmp_path):
    return JsonStore(
        runtime_path=tmp_path / "data.json",
        seed_path=ROOT / "data" / "demo_seed.json",
        uploads_dir=tmp_path / "uploads",
    )


# --- disponibilidad_filtered ---

def test_disponibilidad_filtered_by_centro():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        rows = store.disponibilidad_filtered(centro_id=1)
        assert len(rows) > 0
        assert all(item["medico"]["centro_id"] == 1 for item in rows)


def test_disponibilidad_filtered_by_especialidad():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        rows = store.disponibilidad_filtered(especialidad_id=3)
        assert len(rows) > 0
        assert all(item["medico"]["especialidad_id"] == 3 for item in rows)


def test_disponibilidad_filtered_by_medico():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        rows = store.disponibilidad_filtered(medico_id=1)
        assert len(rows) >= 1
        assert all(item["medico"]["id"] == 1 for item in rows)


def test_disponibilidad_filtered_combined():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        rows = store.disponibilidad_filtered(centro_id=2, especialidad_id=4)
        assert len(rows) == 1
        assert rows[0]["medico"]["id"] == 4
        assert rows[0]["medico"]["centro_id"] == 2
        assert rows[0]["medico"]["especialidad_id"] == 4


def test_disponibilidad_filtered_no_match():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        rows = store.disponibilidad_filtered(centro_id=999)
        assert rows == []


def test_disponibilidad_filtered_no_params_returns_all():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        all_rows = store.disponibilidad_filtered()
        assert len(all_rows) > 0


# --- create_agenda ---

def test_create_agenda():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        agenda = store.create_agenda({
            "medico_id": 1,
            "dia_semana": "Sabado",
            "hora_inicio": "08:00",
            "hora_fin": "12:00",
            "duracion_minutos": 30,
            "cupo_diario": 8,
        })
        assert agenda["medico_id"] == 1
        assert agenda["dia_semana"] == "Sabado"
        assert agenda["hora_inicio"] == "08:00"
        assert agenda["cupo_diario"] == 8
        assert "id" in agenda


def test_create_agenda_invalid_medico():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        try:
            store.create_agenda({
                "medico_id": 9999,
                "dia_semana": "Lunes",
                "hora_inicio": "08:00",
                "hora_fin": "12:00",
                "duracion_minutos": 30,
                "cupo_diario": 8,
            })
            assert False, "Deberia haber lanzado ValueError"
        except ValueError as e:
            assert "medico" in str(e).lower()


# --- import_agendas ---

def test_import_agendas_batch():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        agendas = [
            {"medico_id": 1, "dia_semana": "Sabado", "hora_inicio": "08:00", "hora_fin": "12:00", "duracion_minutos": 30, "cupo_diario": 8},
            {"medico_id": 2, "dia_semana": "Sabado", "hora_inicio": "09:00", "hora_fin": "13:00", "duracion_minutos": 20, "cupo_diario": 10},
        ]
        res = store.import_agendas(agendas)
        assert res["created"] == 2
        assert res["skipped"] == 0
        assert res["errors"] == []


def test_import_agendas_with_errors():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        valid = {"medico_id": 1, "dia_semana": "Sabado", "hora_inicio": "08:00", "hora_fin": "12:00", "duracion_minutos": 30, "cupo_diario": 8}
        invalid = {"medico_id": 9999, "dia_semana": "Lunes"}
        res = store.import_agendas([valid, invalid])
        assert res["created"] == 1
        assert res["skipped"] == 1
        assert len(res["errors"]) == 1


def test_import_agendas_not_list():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        try:
            store.import_agendas({"medico_id": 1})
            assert False, "Deberia haber lanzado ValueError"
        except ValueError:
            pass


# --- calcular_precio ---

def test_calcular_precio_dolor_de_pecho():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        res = store.calcular_precio({"especialidad_id": 4, "motivo": "Dolor de pecho"})
        assert res["estimated_price"] > 0
        assert res["multiplier"] == 1.6
        assert res["range"][0] < res["estimated_price"] < res["range"][1]


def test_calcular_precio_consulta():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        res = store.calcular_precio({"especialidad_id": 4, "motivo": "Consulta odontologica"})
        assert res["estimated_price"] > 0
        assert res["multiplier"] == 1.0


def test_calcular_precio_con_medico():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        res = store.calcular_precio({"medico_id": 1, "motivo": "Control cardiologico"})
        assert "estimated_price" in res
        assert "base_price" in res


def test_calcular_precio_urgencia():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        res = store.calcular_precio({"especialidad_id": 4, "motivo": "Urgencia dental"})
        assert res["multiplier"] == 1.5
        assert res["estimated_price"] > 0


def test_calcular_precio_empty_motivo():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        res = store.calcular_precio({"especialidad_id": 3, "motivo": ""})
        assert res["multiplier"] == 1.0


def test_calcular_precio_invalid_payload():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        try:
            store.calcular_precio("not a dict")
            assert False, "Deberia haber lanzado ValueError"
        except ValueError:
            pass


def test_calcular_precio_medico_no_existe():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        try:
            store.calcular_precio({"medico_id": 9999, "motivo": "test"})
            assert False, "Deberia haber lanzado ValueError"
        except ValueError as e:
            assert "medico" in str(e).lower()


# --- Filtros de dashboard por slug ---

def test_filter_dashboard_by_centro():
    with TemporaryDirectory() as tmp:
        store = _make_store(Path(tmp))
        dashboard = store.dashboard()
        filtered = filter_dashboard_by_centro(dashboard, 1)
        assert len(filtered["centros"]) == 1
        assert filtered["centros"][0]["id"] == 1
        assert all(t["centro_id"] == 1 for t in filtered["turnos"])


def test_centro_id_for_slug_or_host():
    dashboard = {"centros": [{"id": 1, "slug": "hospital-a"}, {"id": 2, "slug": "clinica-b"}]}
    assert centro_id_for_slug_or_host(dashboard, slug="hospital-a") == 1
    assert centro_id_for_slug_or_host(dashboard, slug="clinica-b") == 2
    assert centro_id_for_slug_or_host(dashboard, slug="no-existe") is None
    assert centro_id_for_slug_or_host(dashboard, host="hospital-a.example.com") == 1
    assert centro_id_for_slug_or_host(dashboard, host="other.com") is None
