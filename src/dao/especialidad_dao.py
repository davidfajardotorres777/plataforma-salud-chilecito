from src.dao.base_dao import BaseDAO
from src.models.especialidad import Especialidad


class EspecialidadDAO(BaseDAO):
    table_name = "especialidad"

    def listar(self) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_especialidad, nombre, descripcion, activa
            FROM especialidad
            ORDER BY nombre
            """
        )

    def obtener_por_nombre(self, nombre: str) -> dict | None:
        return self.fetch_one(
            """
            SELECT id_especialidad, nombre, descripcion, activa
            FROM especialidad
            WHERE UPPER(nombre) = UPPER(:nombre)
            """,
            {"nombre": nombre},
        )

    def crear(self, especialidad: Especialidad) -> int:
        return self.execute(
            """
            INSERT INTO especialidad (nombre, descripcion, activa)
            VALUES (:nombre, :descripcion, :activa)
            """,
            {
                "nombre": especialidad.nombre,
                "descripcion": especialidad.descripcion,
                "activa": especialidad.activa,
            },
        )
