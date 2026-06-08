from src.webapp.server import filter_dashboard_by_centro, centro_id_for_slug_or_host


def test_filter_dashboard_by_centro_basic():
    # build a small dashboard sample
    dashboard = {
        "centros": [{"id": 1, "nombre": "A"}, {"id": 2, "nombre": "B"}],
        "medicos": [{"id": 10, "centro_id": 1}, {"id": 20, "centro_id": 2}],
        "pacientes": [{"id": 100}, {"id": 200}],
        "turnos": [{"id": 1, "centro_id": 1, "paciente_id": 100}, {"id": 2, "centro_id": 2, "paciente_id": 200}],
        "disponibilidad": [{"medico": {"id": 10, "centro_id": 1}}, {"medico": {"id": 20, "centro_id": 2}}],
        "documentos": [],
    }

    filtered = filter_dashboard_by_centro(dashboard, 1)
    assert len(filtered["centros"]) == 1
    assert all(m["centro_id"] == 1 for m in filtered["medicos"]) or len(filtered["medicos"]) == 1
    assert all(t["centro_id"] == 1 for t in filtered["turnos"]) and len(filtered["turnos"]) == 1


def test_centro_id_for_slug_or_host():
    dashboard = {"centros": [{"id": 1, "slug": "hospital-a"}, {"id": 2, "slug": "clinica-b"}]}
    assert centro_id_for_slug_or_host(dashboard, slug="hospital-a") == 1
    assert centro_id_for_slug_or_host(dashboard, host="hospital-a.example.com") == 1
    assert centro_id_for_slug_or_host(dashboard, host="clinica-b.local") == 2
    assert centro_id_for_slug_or_host(dashboard, slug="not-found") is None
