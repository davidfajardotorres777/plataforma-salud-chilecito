import time
from report_generator import ReportGenerator
from dao_mongodb import SaludDAO

# We need to setup some data to benchmark
import pymongo
from datetime import datetime, timedelta
import random

dao = SaludDAO()
db = dao._get_db()

# Clean up
db["turnos"].delete_many({"test_benchmark": True})
db["medicos"].delete_many({"test_benchmark": True})
db["especialidades"].delete_many({"test_benchmark": True})

# Insert especialidades
especialidad_ids = []
for i in range(10):
    res = db["especialidades"].insert_one({"nombre": f"Especialidad {i}", "test_benchmark": True})
    especialidad_ids.append(res.inserted_id)

# Insert medicos
medico_ids = []
for i in range(50):
    res = db["medicos"].insert_one({
        "nombre": f"Medico {i}",
        "especialidad_id": random.choice(especialidad_ids),
        "test_benchmark": True
    })
    medico_ids.append(res.inserted_id)

# Insert turnos
turnos = []
for i in range(1000):
    turnos.append({
        "fecha_turno": datetime(2024, 1, 15),
        "estado": "completado",
        "precio_consulta": random.randint(100, 500),
        "medico_id": random.choice(medico_ids),
        "test_benchmark": True
    })
db["turnos"].insert_many(turnos)

gen = ReportGenerator()

start = time.time()
res = gen.generar_reporte_financiero(fecha_inicio="2024-01-01", fecha_fin="2024-01-31")
end = time.time()

print(f"Time taken: {end - start:.4f} seconds")
print(f"Total ingresos: {res['estadisticas']['total_ingresos']}")

# Clean up
db["turnos"].delete_many({"test_benchmark": True})
db["medicos"].delete_many({"test_benchmark": True})
db["especialidades"].delete_many({"test_benchmark": True})
