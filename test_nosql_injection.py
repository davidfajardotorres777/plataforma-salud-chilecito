import pytest
from report_generator import ReportGenerator
from unittest.mock import MagicMock

def test_nosql_injection_turnos():
    rg = ReportGenerator()
    rg.dao = MagicMock()
    mock_db = MagicMock()
    rg.dao._get_db.return_value = {"turnos": mock_db}
    malicious_payload = {"$ne": "null"}
    rg.generar_reporte_turnos(centro_id=malicious_payload)
    mock_db.find.assert_called_once()
    query = mock_db.find.call_args[0][0]
    assert query["centro_id"] == str(malicious_payload)
    assert not isinstance(query["centro_id"], dict)

def test_nosql_injection_pacientes():
    rg = ReportGenerator()
    rg.dao = MagicMock()
    mock_db = MagicMock()
    rg.dao._get_db.return_value = {"pacientes": mock_db}
    malicious_payload = {"$ne": "null"}
    rg.generar_reporte_pacientes(centro_id=malicious_payload)
    mock_db.find.assert_called_once()
    query = mock_db.find.call_args[0][0]
    assert query["centro_id"] == str(malicious_payload)

def test_nosql_injection_medicos():
    rg = ReportGenerator()
    rg.dao = MagicMock()
    mock_db_medicos = MagicMock()
    mock_db_especialidades = MagicMock()
    mock_db_turnos = MagicMock()

    def get_collection(name):
        if name == "medicos": return mock_db_medicos
        if name == "especialidades": return mock_db_especialidades
        if name == "turnos": return mock_db_turnos
        return MagicMock()

    db_mock = MagicMock()
    db_mock.__getitem__.side_effect = get_collection
    rg.dao._get_db.return_value = db_mock

    malicious_payload = {"$ne": "null"}
    rg.generar_reporte_medicos(centro_id=malicious_payload)

    mock_db_medicos.find.assert_called_once()
    query = mock_db_medicos.find.call_args[0][0]

    assert query["centro_id"] == str(malicious_payload)
