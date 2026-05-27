from src.dao.base_dao import BaseDAO
from src.models.medico import Medico


class MedicoDAO(BaseDAO):
    table_name = "medico"

    def listar_por_centro(self, id_centro: int) -> list[dict]:
        return self.fetch_all(
            """
            SELECT m.id_medico, m.nombre, m.matricula, e.nombre AS especialidad,
                   c.nombre AS centro, m.telefono, m.email, m.activo
            FROM medico m
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            JOIN centro_salud c ON c.id_centro = m.id_centro
            WHERE m.id_centro = :id_centro
            ORDER BY e.nombre, m.nombre
            """,
            {"id_centro": id_centro},
        )

    def buscar_por_especialidad(self, especialidad: str) -> list[dict]:
        return self.fetch_all(
            """
            SELECT m.id_medico, m.nombre, m.matricula, e.nombre AS especialidad,
                   c.nombre AS centro, c.distrito
            FROM medico m
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            JOIN centro_salud c ON c.id_centro = m.id_centro
            WHERE UPPER(e.nombre) LIKE '%' || UPPER(:especialidad) || '%'
              AND m.activo = 'S'
            ORDER BY c.distrito, c.nombre, m.nombre
            """,
            {"especialidad": especialidad},
        )

    def crear(self, medico: Medico) -> int:
        return self.execute(
            """
            INSERT INTO medico
              (nombre, matricula, telefono, email, id_especialidad, id_centro, activo)
            VALUES
              (:nombre, :matricula, :telefono, :email, :id_especialidad, :id_centro, :activo)
            """,
            {
                "nombre": medico.nombre,
                "matricula": medico.matricula,
                "telefono": medico.telefono,
                "email": medico.email,
                "id_especialidad": medico.id_especialidad,
                "id_centro": medico.id_centro,
                "activo": medico.activo,
            },
        )
