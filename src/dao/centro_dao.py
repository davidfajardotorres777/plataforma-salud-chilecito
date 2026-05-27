from src.dao.base_dao import BaseDAO
from src.models.centro import CentroSalud


class CentroDAO(BaseDAO):
    table_name = "centro_salud"

    def listar(self, distrito: str | None = None) -> list[dict]:
        if distrito:
            return self.fetch_all(
                """
                SELECT id_centro, nombre, direccion, distrito, telefono, tipo, email, activo
                FROM centro_salud
                WHERE UPPER(distrito) = UPPER(:distrito)
                ORDER BY nombre
                """,
                {"distrito": distrito},
            )

        return self.fetch_all(
            """
            SELECT id_centro, nombre, direccion, distrito, telefono, tipo, email, activo
            FROM centro_salud
            ORDER BY distrito, nombre
            """
        )

    def crear(self, centro: CentroSalud) -> int:
        return self.execute(
            """
            INSERT INTO centro_salud (nombre, direccion, distrito, telefono, tipo, email, activo)
            VALUES (:nombre, :direccion, :distrito, :telefono, :tipo, :email, :activo)
            """,
            {
                "nombre": centro.nombre,
                "direccion": centro.direccion,
                "distrito": centro.distrito,
                "telefono": centro.telefono,
                "tipo": centro.tipo,
                "email": centro.email,
                "activo": centro.activo,
            },
        )
