import time
from datetime import datetime
import mongomock
from bson import ObjectId
from report_generator import ReportGenerator

def setup_db(num_turnos):
    client = mongomock.MongoClient()
    db = client["salud_test_benchmark"]

    # Insertar especialidades
    esp_ids = []
    for i in range(20):
        res = db.especialidades.insert_one({"nombre": f"Especialidad {i}"})
        esp_ids.append(res.inserted_id)

    # Insertar médicos
    medico_ids = []
    for i in range(100):
        res = db.medicos.insert_one({
            "nombre": f"Medico {i}",
            "especialidad_id": esp_ids[i % 20]
        })
        medico_ids.append(res.inserted_id)

    # Insertar turnos
    turnos = []
    for i in range(num_turnos):
        turnos.append({
            "fecha_turno": datetime(2024, 1, 1),
            "estado": "completado",
            "medico_id": medico_ids[i % 100],
            "centro_id": "centro1",
            "precio_consulta": 100
        })
    db.turnos.insert_many(turnos)

    return db, client

def run_benchmark(num_turnos):
    db, client = setup_db(num_turnos)

    # Override db in report generator
    rg = ReportGenerator()
    rg.dao._get_db = lambda: db

    start_time = time.time()
    res = rg.generar_reporte_turnos(fecha_inicio="2024-01-01", fecha_fin="2024-01-02")
    end_time = time.time()

    print(f"Time taken for {num_turnos} turnos (generar_reporte_turnos): {end_time - start_time:.4f} seconds")

    start_time = time.time()
    res = rg.generar_reporte_financiero(fecha_inicio="2024-01-01", fecha_fin="2024-01-02")
    end_time = time.time()

    print(f"Time taken for {num_turnos} turnos (generar_reporte_financiero): {end_time - start_time:.4f} seconds")

    client.close()

if __name__ == "__main__":
    for i in [1000, 5000, 10000]:
        run_benchmark(i)
