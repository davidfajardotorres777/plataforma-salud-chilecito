from src.dao.base_dao import BaseDAO
from src.models.turno import Turno


class TurnoDAO(BaseDAO):
    table_name = "turno"

    def listar_proximos(self, limite: int = 20) -> list[dict]:
        return self.fetch_all(
            """
            SELECT *
            FROM (
                SELECT t.id_turno, t.fecha_turno, t.estado, t.precio_consulta,
                       p.nombre AS paciente, p.dni,
                       m.nombre AS medico, c.nombre AS centro, c.distrito
                FROM turno t
                JOIN paciente p ON p.id_paciente = t.id_paciente
                JOIN medico m ON m.id_medico = t.id_medico
                JOIN centro_salud c ON c.id_centro = t.id_centro
                WHERE t.fecha_turno >= SYSDATE
                ORDER BY t.fecha_turno
            )
            WHERE ROWNUM <= :limite
            """,
            {"limite": limite},
        )

    def reservar(self, turno: Turno) -> int:
        return self.execute(
            """
            INSERT INTO turno
              (id_paciente, id_medico, id_centro, fecha_turno, estado, precio_consulta, observaciones)
            VALUES
              (:id_paciente, :id_medico, :id_centro, :fecha_turno, :estado, :precio_consulta, :observaciones)
            """,
            {
                "id_paciente": turno.id_paciente,
                "id_medico": turno.id_medico,
                "id_centro": turno.id_centro,
                "fecha_turno": turno.fecha_turno,
                "estado": turno.estado,
                "precio_consulta": turno.precio_consulta,
                "observaciones": turno.observaciones,
            },
        )

    def cambiar_estado(self, id_turno: int, estado_nuevo: str) -> int:
        return self.execute(
            """
            UPDATE turno
            SET estado = :estado_nuevo
            WHERE id_turno = :id_turno
            """,
            {"id_turno": id_turno, "estado_nuevo": estado_nuevo},
        )

    def disponibilidad_por_medico(self, id_medico: int) -> list[dict]:
        return self.fetch_all(
            """
            SELECT a.dia_semana, a.hora_inicio, a.hora_fin, a.cupo_diario,
                   COUNT(t.id_turno) AS turnos_tomados
            FROM agenda_medico a
            LEFT JOIN turno t
              ON t.id_medico = a.id_medico
             AND t.estado IN ('PENDIENTE', 'CONFIRMADO')
            WHERE a.id_medico = :id_medico
            GROUP BY a.dia_semana, a.hora_inicio, a.hora_fin, a.cupo_diario
            ORDER BY a.dia_semana, a.hora_inicio
            """,
            {"id_medico": id_medico},
        )
