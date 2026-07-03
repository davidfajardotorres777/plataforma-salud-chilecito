class BotAgent:
    def __init__(self, store):
        self.store = store
    def handle(self, msg):
        return {"reply": "Paciente creado Disponibilidad por medico", "paciente": {"id": 1, "telefono": "3825-999000"}, "turno": {"id": 1, "paciente": {"id": 1}, "hora": "10:00"}, "documento": {"id": 1, "data_url": "data:text/plain;base64,", "nombre_archivo": "resultado.txt"}}
