from src.dao.base_dao import BaseDAO
from src.models.paciente import Paciente


class PacienteDAO(BaseDAO):
    table_name = "paciente"

    def obtener_por_dni(self, dni: str) -> dict | None:
        return self.fetch_one(
            """
            SELECT id_paciente, dni, nombre, fecha_nacimiento, telefono, email,
                   obra_social, distrito, fecha_alta
            FROM paciente
            WHERE dni = :dni
            """,
            {"dni": dni},
        )

    def crear(self, paciente: Paciente) -> int:
        return self.execute(
            """
            INSERT INTO paciente
              (dni, nombre, fecha_nacimiento, telefono, email, obra_social, distrito)
            VALUES
              (:dni, :nombre, :fecha_nacimiento, :telefono, :email, :obra_social, :distrito)
            """,
            {
                "dni": paciente.dni,
                "nombre": paciente.nombre,
                "fecha_nacimiento": paciente.fecha_nacimiento,
                "telefono": paciente.telefono,
                "email": paciente.email,
                "obra_social": paciente.obra_social,
                "distrito": paciente.distrito,
            },
        )

    def actualizar_contacto(self, id_paciente: int, telefono: str, email: str | None = None) -> int:
        return self.execute(
            """
            UPDATE paciente
            SET telefono = :telefono,
                email = COALESCE(:email, email)
            WHERE id_paciente = :id_paciente
            """,
            {"id_paciente": id_paciente, "telefono": telefono, "email": email},
        )
