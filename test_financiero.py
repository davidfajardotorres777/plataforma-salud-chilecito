import pytest
from unittest.mock import MagicMock
from report_generator import ReportGenerator
import json

def test_generar_reporte_financiero_n_plus_1_optimization():
    gen = ReportGenerator()

    # Mocking the DAO
    mock_db = MagicMock()

    # Simulate DB state
    turnos_data = [
        {"medico_id": "med1", "precio_consulta": 100, "estado": "completado"},
        {"medico_id": "med1", "precio_consulta": 100, "estado": "completado"},
        {"medico_id": "med2", "precio_consulta": 150, "estado": "completado"},
    ]
    medicos_data = [
        {"_id": "med1", "especialidad_id": "esp1"},
        {"_id": "med2", "especialidad_id": "esp2"},
    ]
    especialidades_data = [
        {"_id": "esp1", "nombre": "Cardiología"},
        {"_id": "esp2", "nombre": "Pediatría"},
    ]

    mock_db.__getitem__.return_value.find.return_value = turnos_data

    # We need to setup a mock for db["turnos"].find, db["medicos"].find, db["especialidades"].find
    # Track the number of calls to find_one and find to detect N+1
    find_one_calls = 0
    find_calls = 0

    def get_collection(name):
        mock_col = MagicMock()
        if name == "turnos":
            mock_col.find.return_value = turnos_data
        elif name == "medicos":
            def side_effect_find_one(*args, **kwargs):
                nonlocal find_one_calls
                find_one_calls += 1
                query = args[0]
                if "_id" in query:
                    for medico in medicos_data:
                        if medico["_id"] == query["_id"]:
                            return medico
                return None
            def side_effect_find(*args, **kwargs):
                nonlocal find_calls
                find_calls += 1
                query = args[0]
                if "_id" in query and "$in" in query["_id"]:
                    return [m for m in medicos_data if m["_id"] in query["_id"]["$in"]]
                return medicos_data
            mock_col.find_one.side_effect = side_effect_find_one
            mock_col.find.side_effect = side_effect_find
        elif name == "especialidades":
            def side_effect_find_one(*args, **kwargs):
                nonlocal find_one_calls
                find_one_calls += 1
                query = args[0]
                if "_id" in query:
                    for esp in especialidades_data:
                        if esp["_id"] == query["_id"]:
                            return esp
                return None
            def side_effect_find(*args, **kwargs):
                nonlocal find_calls
                find_calls += 1
                query = args[0]
                if "_id" in query and "$in" in query["_id"]:
                    return [e for e in especialidades_data if e["_id"] in query["_id"]["$in"]]
                return especialidades_data
            mock_col.find_one.side_effect = side_effect_find_one
            mock_col.find.side_effect = side_effect_find

        return mock_col

    mock_db.__getitem__.side_effect = get_collection

    gen.dao = MagicMock()
    gen.dao._get_db = MagicMock(return_value=mock_db)

    res = gen.generar_reporte_financiero(fecha_inicio="2024-01-01", fecha_fin="2024-01-31")

    print(res["estadisticas"])
    assert res["estadisticas"]["total_ingresos"] == 350
    assert res["estadisticas"]["ingresos_por_especialidad"] == {"Cardiología": 200.0, "Pediatría": 150.0}

    # We want find_one calls to be zero ideally, and find calls to be minimal (no N+1)
    print(f"find_one calls: {find_one_calls}")
    print(f"find calls: {find_calls}")

    return find_one_calls, find_calls

if __name__ == "__main__":
    test_generar_reporte_financiero_n_plus_1_optimization()
