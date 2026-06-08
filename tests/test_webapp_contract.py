import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from src.webapp.bot_agent import BotAgent
from src.webapp.store import JsonStore


ROOT = Path(__file__).resolve().parents[1]


def test_demo_seed_has_required_collections():
    data = json.loads((ROOT / "data" / "demo_seed.json").read_text(encoding="utf-8"))
    for name in ["centros", "especialidades", "medicos", "pacientes", "turnos", "documentos", "agendas", "tarifas"]:
        assert name in data
        assert isinstance(data[name], list)
    assert len(data["centros"]) >= 4
    assert len(data["medicos"]) >= 4
    assert len(data["agendas"]) >= 4
    assert len(data["tarifas"]) >= 4


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
        assert "disponibilidad" in dashboard
        assert doc["tamano_bytes"] == 10
        assert dashboard["metricas"]["pacientes"] == 4
        assert dashboard["metricas"]["documentos"] == 1


def test_json_store_exposes_availability_and_estimates_price():
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        store = JsonStore(
            runtime_path=base / "runtime.json",
            seed_path=ROOT / "data" / "demo_seed.json",
            uploads_dir=base / "uploads",
        )
        dashboard = store.dashboard()
        odontologia = next(item for item in dashboard["disponibilidad"] if item["medico"]["id"] == 4)
        turno = store.create_turno(
            {
                "paciente_id": 1,
                "medico_id": 4,
                "fecha": "2026-06-19",
                "hora": "15:30",
                "estado": "PENDIENTE",
                "motivo": "Dolor dental",
            }
        )

        assert odontologia["dia_semana"] == "Viernes"
        assert odontologia["precio_estimado"] == 12000
        assert turno["precio"] == 12000


def test_json_store_updates_patient_and_turno_then_deletes_turno():
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        store = JsonStore(
            runtime_path=base / "runtime.json",
            seed_path=ROOT / "data" / "demo_seed.json",
            uploads_dir=base / "uploads",
        )
        paciente = store.update_patient(
            1,
            {
                "dni": "40111223",
                "nombre": "Juan Perez Corregido",
                "telefono": "3825-999999",
                "obra_social": "APOS",
                "distrito": "Chilecito",
            },
        )
        turno = store.update_turno(
            1,
            {
                "paciente_id": paciente["id"],
                "medico_id": 2,
                "fecha": "2026-06-11",
                "hora": "11:00",
                "estado": "CONFIRMADO",
                "precio": 0,
                "motivo": "Horario corregido",
            },
        )
        deleted = store.delete_turno(turno["id"])

        assert paciente["nombre"] == "Juan Perez Corregido"
        assert turno["hora"] == "11:00"
        assert deleted["id"] == 1
        assert all(t["id"] != 1 for t in store.dashboard()["turnos"])


def test_json_store_returns_document_preview_content():
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        store = JsonStore(
            runtime_path=base / "runtime.json",
            seed_path=ROOT / "data" / "demo_seed.json",
            uploads_dir=base / "uploads",
        )
        doc = store.save_document(
            {
                "paciente_id": 1,
                "tipo": "ESTUDIO",
                "nombre_archivo": "estudio.txt",
                "mime_type": "text/plain",
                "contenido_base64": base64.b64encode(b"resultado normal").decode("ascii"),
            }
        )
        preview = store.get_document(doc["id"])

        assert preview["mime_type"] == "text/plain"
        assert preview["contenido_base64"]
        assert preview["data_url"].startswith("data:text/plain;base64,")


def test_json_store_creates_and_updates_centers():
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        store = JsonStore(
            runtime_path=base / "runtime.json",
            seed_path=ROOT / "data" / "demo_seed.json",
            uploads_dir=base / "uploads",
        )
        centro = store.create_center(
            {
                "nombre": "Centro Demo",
                "direccion": "Calle Publica 123",
                "distrito": "Vichigasta",
                "telefono": "3825-777777",
                "tipo": "PUBLICO",
            }
        )
        actualizado = store.update_center(
            centro["id"],
            {
                "nombre": "Centro Demo Editado",
                "direccion": "Calle Publica 456",
                "distrito": "Vichigasta",
                "telefono": "3825-888888",
                "tipo": "MIXTO",
            },
        )

        dashboard = store.dashboard()
        assert centro["id"] == actualizado["id"]
        assert actualizado["nombre"] == "Centro Demo Editado"
        assert dashboard["metricas"]["centros"] == 5


def test_bot_agent_operates_platform_by_conversation():
    with TemporaryDirectory() as tmp:
        base = Path(tmp)
        store = JsonStore(
            runtime_path=base / "runtime.json",
            seed_path=ROOT / "data" / "demo_seed.json",
            uploads_dir=base / "uploads",
        )
        agent = BotAgent(store)

        created_patient = agent.handle(
            "crear paciente nombre Ana Diaz dni 50999111 telefono 3825-111222 distrito Chilecito obra social APOS"
        )
        patient_id = created_patient["paciente"]["id"]
        updated_patient = agent.handle(f"editar paciente {patient_id} telefono 3825-999000 distrito Nonogasta")
        created_turno = agent.handle(
            f"crear turno paciente {patient_id} medico 1 fecha 2026-06-20 hora 09:30 motivo control"
        )
        turno_id = created_turno["turno"]["id"]
        updated_turno = agent.handle(f"editar turno {turno_id} hora 10:00 motivo control reprogramado")
        deleted_turno = agent.handle(f"eliminar turno {turno_id}")
        created_document = agent.handle(
            f"crear documento paciente {patient_id} tipo ESTUDIO archivo resultado.txt contenido Resultado normal"
        )
        viewed_document = agent.handle(f"ver documento {created_document['documento']['id']}")
        availability = agent.handle("mostrar horarios disponibles y precios")

        assert "Paciente creado" in created_patient["reply"]
        assert updated_patient["paciente"]["telefono"] == "3825-999000"
        assert created_turno["turno"]["paciente"]["id"] == patient_id
        assert updated_turno["turno"]["hora"] == "10:00"
        assert deleted_turno["turno"]["id"] == turno_id
        assert created_document["documento"]["data_url"].startswith("data:text/plain;base64,")
        assert viewed_document["documento"]["nombre_archivo"] == "resultado.txt"
        assert "Disponibilidad por medico" in availability["reply"]


def test_static_browser_app_files_exist():
    static = ROOT / "src" / "webapp" / "static"
    assert (static / "index.html").exists()
    assert (static / "bot.html").exists()
    assert (static / "styles.css").exists()
    assert (static / "app.js").exists()
    assert (static / "bot.js").exists()
    assert "Nuevo turno" in (static / "index.html").read_text(encoding="utf-8")
    assert "Guardar centro" in (static / "index.html").read_text(encoding="utf-8")
    assert "Guardar paciente" in (static / "index.html").read_text(encoding="utf-8")
    assert "Abrir Bot IA" in (static / "index.html").read_text(encoding="utf-8")
    assert "Bot IA operativo" in (static / "bot.html").read_text(encoding="utf-8")
    assert "documentDialog" in (static / "index.html").read_text(encoding="utf-8")
    assert "disponibilidadList" in (static / "index.html").read_text(encoding="utf-8")
    assert "/api/dashboard" in (static / "app.js").read_text(encoding="utf-8")
    assert "renderDisponibilidad" in (static / "app.js").read_text(encoding="utf-8")
    assert "/api/centros" in (static / "app.js").read_text(encoding="utf-8")
    assert "/api/pacientes/" in (static / "app.js").read_text(encoding="utf-8")
    assert "/api/documentos/" in (static / "app.js").read_text(encoding="utf-8")
    assert "/api/bot" in (static / "bot.js").read_text(encoding="utf-8")
    assert "/eliminar" in (static / "app.js").read_text(encoding="utf-8")
