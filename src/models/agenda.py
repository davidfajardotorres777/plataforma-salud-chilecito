from dataclasses import dataclass


@dataclass(slots=True)
class AgendaMedico:
    id_medico: int
    dia_semana: str
    hora_inicio: str
    hora_fin: str
    duracion_minutos: int = 30
    cupo_diario: int = 16
    id_agenda: int | None = None
