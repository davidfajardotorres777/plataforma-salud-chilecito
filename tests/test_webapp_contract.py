import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from src.webapp.store import JsonStore


ROOT = Path(__file__).resolve().parents[1]


def test_demo_seed_has_required_collections():
    data = json.loads((ROOT / "data" / "demo_seed.json").read_text(encoding="utf-8"))
    for name in ["centros", "especialidades", "medicos", "pacientes", "turnos", "documentos"]:
        assert name in data
        assert isinstance(data[name], list)
    assert len(data["centros"]) >= 4
    assert len(data["medicos"]) >= 4


def test_json_store_creates_patient_turno_and_document():
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        store = JsonStore(
            runtime_path=base / "runtime.json",
            seed_path=ROOT / "data" / "demo_seed.json",
            uploads_dir=base / "uploads",
        )
        paciente = store.create_patient(
            {
                "dni": "50999888",
                "nombre": "Paciente Demo",
                "telefono": "3825-111111",
                "distrito": "Chilecito",
                "obra_social": "APOS",
            }
        )
        turno = store.create_turno(
            {
                "paciente_id": paciente["id"],
                "medico_id": 1,
                "fecha": "2026-06-10",
                "hora": "09:00",
                "estado": "CONFIRMADO",
                "precio": 0,
                "motivo": "Control de prueba",
            }
        )
        doc = store.save_document(
            {
                "paciente_id": paciente["id"],
                "tipo": "ORDEN",
                "nombre_archivo": "orden.txt",
                "contenido_base64": base64.b64encode(b"orden demo").decode("ascii"),
            }
        )

        dashboard = store.dashboard()
        assert paciente["dni"] == "50999888"
        assert turno["paciente"]["nombre"] == "Paciente Demo"
        assert doc["tamano_bytes"] == 10
        assert dashboard["metricas"]["pacientes"] == 4
        assert dashboard["metricas"]["documentos"] == 1


def test_static_browser_app_files_exist():
    static = ROOT / "src" / "webapp" / "static"
    assert (static / "index.html").exists()
    assert (static / "styles.css").exists()
    assert (static / "app.js").exists()
    assert "Nuevo turno" in (static / "index.html").read_text(encoding="utf-8")
    assert "/api/dashboard" in (static / "app.js").read_text(encoding="utf-8")
