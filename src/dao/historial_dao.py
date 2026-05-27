from src.dao.base_dao import BaseDAO
from src.models.historial import HistorialClinico


class HistorialDAO(BaseDAO):
    table_name = "historial_clinico"

    def listar_por_paciente(self, id_paciente: int) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_historial, id_paciente, id_turno, fecha_registro,
                   diagnostico, indicaciones, profesional
            FROM historial_clinico
            WHERE id_paciente = :id_paciente
            ORDER BY fecha_registro DESC
            """,
            {"id_paciente": id_paciente},
        )

    def registrar(self, historial: HistorialClinico) -> int:
        return self.execute(
            """
            INSERT INTO historial_clinico
              (id_paciente, id_turno, diagnostico, indicaciones, profesional)
            VALUES
              (:id_paciente, :id_turno, :diagnostico, :indicaciones, :profesional)
            """,
            {
                "id_paciente": historial.id_paciente,
                "id_turno": historial.id_turno,
                "diagnostico": historial.diagnostico,
                "indicaciones": historial.indicaciones,
                "profesional": historial.profesional,
            },
        )
