from src.dao.base_dao import BaseDAO
from src.models.agenda import AgendaMedico


class AgendaDAO(BaseDAO):
    table_name = "agenda_medico"

    def listar_por_medico(self, id_medico: int) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_agenda, id_medico, dia_semana, hora_inicio, hora_fin,
                   duracion_minutos, cupo_diario
            FROM agenda_medico
            WHERE id_medico = :id_medico
            ORDER BY dia_semana, hora_inicio
            """,
            {"id_medico": id_medico},
        )

    def crear(self, agenda: AgendaMedico) -> int:
        return self.execute(
            """
            INSERT INTO agenda_medico
              (id_medico, dia_semana, hora_inicio, hora_fin, duracion_minutos, cupo_diario)
            VALUES
              (:id_medico, :dia_semana, :hora_inicio, :hora_fin, :duracion_minutos, :cupo_diario)
            """,
            {
                "id_medico": agenda.id_medico,
                "dia_semana": agenda.dia_semana,
                "hora_inicio": agenda.hora_inicio,
                "hora_fin": agenda.hora_fin,
                "duracion_minutos": agenda.duracion_minutos,
                "cupo_diario": agenda.cupo_diario,
            },
        )
