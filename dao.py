"""
SaludDAO - Capa de acceso a datos para Plataforma Salud Chilecito
=================================================================
Concentra todas las operaciones contra Oracle en una sola clase.
Accesible desde git y desde Jupyter Notebook.

Uso:
    from dao import SaludDAO

    dao = SaludDAO()
    centros = dao.listar_centros()
    dao.cerrar()
"""

from contextlib import contextmanager
from typing import Any

from config_vars import get_db_config


class SaludDAO:
    """Interfaz principal contra Oracle para el dominio de salud."""

    def __init__(self):
        config = get_db_config()
        self._config = config
        self._oracledb = None
        self._dsn = f"{config['host']}:{config['port']}/{config['service']}"

    def _get_driver(self):
        if self._oracledb is None:
            try:
                import oracledb
                self._oracledb = oracledb
            except ImportError:
                raise RuntimeError(
                    "Falta instalar python-oracledb. Ejecuta: pip install -r libs.txt"
                )
        return self._oracledb

    @contextmanager
    def connection(self):
        oracledb = self._get_driver()
        conn = oracledb.connect(
            user=self._config["user"],
            password=self._config["password"],
            dsn=self._dsn,
        )
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def cursor(self):
        with self.connection() as conn:
            cur = conn.cursor()
            try:
                yield conn, cur
            finally:
                cur.close()

    def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self.cursor() as (_, cur):
            cur.execute(sql, params or {})
            columns = [col[0].lower() for col in cur.description]
            return [dict(zip(columns, row)) for row in cur.fetchall()]

    def fetch_one(self, sql: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        rows = self.fetch_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: dict[str, Any] | list[dict[str, Any]] | None = None) -> int:
        with self.cursor() as (conn, cur):
            if isinstance(params, list):
                cur.executemany(sql, params)
            else:
                cur.execute(sql, params or {})
            affected = cur.rowcount
            conn.commit()
            return affected

    def ping(self) -> str:
        row = self.fetch_one("SELECT 'OK' AS status FROM dual")
        return str(row["status"]) if row else "SIN_RESPUESTA"

    def contar(self, tabla: str) -> int:
        row = self.fetch_one(f"SELECT COUNT(*) AS total FROM {tabla}")
        return int(row["total"]) if row else 0

    # ======================================================================
    # CENTROS DE SALUD
    # ======================================================================

    def listar_centros(self, distrito: str | None = None) -> list[dict]:
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

    def crear_centro(
        self, nombre: str, direccion: str, distrito: str, tipo: str,
        telefono: str | None = None, email: str | None = None, activo: str = "S"
    ) -> int:
        return self.execute(
            """
            INSERT INTO centro_salud (nombre, direccion, distrito, telefono, tipo, email, activo)
            VALUES (:nombre, :direccion, :distrito, :telefono, :tipo, :email, :activo)
            """,
            {
                "nombre": nombre, "direccion": direccion, "distrito": distrito,
                "telefono": telefono, "tipo": tipo, "email": email, "activo": activo,
            },
        )

    # ======================================================================
    # ESPECIALIDADES
    # ======================================================================

    def listar_especialidades(self) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_especialidad, nombre, descripcion, activa
            FROM especialidad
            ORDER BY nombre
            """
        )

    def obtener_especialidad_por_nombre(self, nombre: str) -> dict | None:
        return self.fetch_one(
            """
            SELECT id_especialidad, nombre, descripcion, activa
            FROM especialidad
            WHERE UPPER(nombre) = UPPER(:nombre)
            """,
            {"nombre": nombre},
        )

    def crear_especialidad(self, nombre: str, descripcion: str | None = None, activa: str = "S") -> int:
        return self.execute(
            """
            INSERT INTO especialidad (nombre, descripcion, activa)
            VALUES (:nombre, :descripcion, :activa)
            """,
            {"nombre": nombre, "descripcion": descripcion, "activa": activa},
        )

    # ======================================================================
    # MEDICOS
    # ======================================================================

    def listar_medicos_por_centro(self, id_centro: int) -> list[dict]:
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

    def buscar_medicos_por_especialidad(self, especialidad: str) -> list[dict]:
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

    def crear_medico(
        self, nombre: str, matricula: str, id_especialidad: int, id_centro: int,
        telefono: str | None = None, email: str | None = None, activo: str = "S"
    ) -> int:
        return self.execute(
            """
            INSERT INTO medico
              (nombre, matricula, telefono, email, id_especialidad, id_centro, activo)
            VALUES
              (:nombre, :matricula, :telefono, :email, :id_especialidad, :id_centro, :activo)
            """,
            {
                "nombre": nombre, "matricula": matricula, "telefono": telefono,
                "email": email, "id_especialidad": id_especialidad,
                "id_centro": id_centro, "activo": activo,
            },
        )

    # ======================================================================
    # PACIENTES
    # ======================================================================

    def obtener_paciente_por_dni(self, dni: str) -> dict | None:
        return self.fetch_one(
            """
            SELECT id_paciente, dni, nombre, fecha_nacimiento, telefono, email,
                   obra_social, distrito, fecha_alta
            FROM paciente
            WHERE dni = :dni
            """,
            {"dni": dni},
        )

    def listar_pacientes(self) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_paciente, dni, nombre, fecha_nacimiento, telefono, email,
                   obra_social, distrito, fecha_alta
            FROM paciente
            ORDER BY nombre
            """
        )

    def crear_paciente(
        self, dni: str, nombre: str, fecha_nacimiento=None,
        telefono: str | None = None, email: str | None = None,
        obra_social: str | None = None, distrito: str | None = None
    ) -> int:
        return self.execute(
            """
            INSERT INTO paciente
              (dni, nombre, fecha_nacimiento, telefono, email, obra_social, distrito)
            VALUES
              (:dni, :nombre, :fecha_nacimiento, :telefono, :email, :obra_social, :distrito)
            """,
            {
                "dni": dni, "nombre": nombre, "fecha_nacimiento": fecha_nacimiento,
                "telefono": telefono, "email": email, "obra_social": obra_social,
                "distrito": distrito,
            },
        )

    def actualizar_contacto_paciente(self, id_paciente: int, telefono: str, email: str | None = None) -> int:
        return self.execute(
            """
            UPDATE paciente
            SET telefono = :telefono,
                email = COALESCE(:email, email)
            WHERE id_paciente = :id_paciente
            """,
            {"id_paciente": id_paciente, "telefono": telefono, "email": email},
        )

    # ======================================================================
    # AGENDA MEDICO
    # ======================================================================

    def listar_agenda_por_medico(self, id_medico: int) -> list[dict]:
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

    def crear_agenda(
        self, id_medico: int, dia_semana: str, hora_inicio: str, hora_fin: str,
        duracion_minutos: int = 30, cupo_diario: int = 16
    ) -> int:
        return self.execute(
            """
            INSERT INTO agenda_medico
              (id_medico, dia_semana, hora_inicio, hora_fin, duracion_minutos, cupo_diario)
            VALUES
              (:id_medico, :dia_semana, :hora_inicio, :hora_fin, :duracion_minutos, :cupo_diario)
            """,
            {
                "id_medico": id_medico, "dia_semana": dia_semana,
                "hora_inicio": hora_inicio, "hora_fin": hora_fin,
                "duracion_minutos": duracion_minutos, "cupo_diario": cupo_diario,
            },
        )

    # ======================================================================
    # TURNOS
    # ======================================================================

    def listar_turnos_proximos(self, limite: int = 20) -> list[dict]:
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

    def reservar_turno(
        self, id_paciente: int, id_medico: int, id_centro: int,
        fecha_turno, estado: str = "PENDIENTE", precio_consulta: float = 0,
        observaciones: str | None = None
    ) -> int:
        return self.execute(
            """
            INSERT INTO turno
              (id_paciente, id_medico, id_centro, fecha_turno, estado, precio_consulta, observaciones)
            VALUES
              (:id_paciente, :id_medico, :id_centro, :fecha_turno, :estado, :precio_consulta, :observaciones)
            """,
            {
                "id_paciente": id_paciente, "id_medico": id_medico,
                "id_centro": id_centro, "fecha_turno": fecha_turno,
                "estado": estado, "precio_consulta": precio_consulta,
                "observaciones": observaciones,
            },
        )

    def cambiar_estado_turno(self, id_turno: int, estado_nuevo: str) -> int:
        return self.execute(
            """
            UPDATE turno
            SET estado = :estado_nuevo
            WHERE id_turno = :id_turno
            """,
            {"id_turno": id_turno, "estado_nuevo": estado_nuevo},
        )

    def eliminar_turno(self, id_turno: int) -> int:
        return self.execute(
            "DELETE FROM turno WHERE id_turno = :id_turno",
            {"id_turno": id_turno},
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

    def calcular_precio_estimado(self, id_centro: int, id_especialidad: int) -> float:
        row = self.fetch_one(
            """
            SELECT precio_base
            FROM centro_especialidad
            WHERE id_centro = :id_centro AND id_especialidad = :id_especialidad
            """,
            {"id_centro": id_centro, "id_especialidad": id_especialidad},
        )
        return float(row["precio_base"]) if row else 0.0

    # ======================================================================
    # HISTORIAL CLINICO
    # ======================================================================

    def listar_historial_por_paciente(self, id_paciente: int) -> list[dict]:
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

    def registrar_historial(
        self, id_paciente: int, diagnostico: str | None = None,
        indicaciones: str | None = None, profesional: str | None = None,
        id_turno: int | None = None
    ) -> int:
        return self.execute(
            """
            INSERT INTO historial_clinico
              (id_paciente, id_turno, diagnostico, indicaciones, profesional)
            VALUES
              (:id_paciente, :id_turno, :diagnostico, :indicaciones, :profesional)
            """,
            {
                "id_paciente": id_paciente, "id_turno": id_turno,
                "diagnostico": diagnostico, "indicaciones": indicaciones,
                "profesional": profesional,
            },
        )

    # ======================================================================
    # DOCUMENTOS DE PACIENTE
    # ======================================================================

    def listar_documentos_por_paciente(self, id_paciente: int) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_documento, id_paciente, tipo_documento, nombre_archivo, creado_en
            FROM documento_paciente
            WHERE id_paciente = :id_paciente
            ORDER BY creado_en DESC
            """,
            {"id_paciente": id_paciente},
        )

    def crear_documento(
        self, id_paciente: int, tipo_documento: str, nombre_archivo: str,
        contenido=None, url_externa: str | None = None
    ) -> int:
        return self.execute(
            """
            INSERT INTO documento_paciente
              (id_paciente, tipo_documento, nombre_archivo, contenido, url_externa)
            VALUES
              (:id_paciente, :tipo_documento, :nombre_archivo, :contenido, :url_externa)
            """,
            {
                "id_paciente": id_paciente, "tipo_documento": tipo_documento,
                "nombre_archivo": nombre_archivo, "contenido": contenido,
                "url_externa": url_externa,
            },
        )

    # ======================================================================
    # SINTOMAS Y ESPECIALIDADES
    # ======================================================================

    def listar_sintomas(self) -> list[dict]:
        return self.fetch_all(
            """
            SELECT s.id_sintoma, s.descripcion, s.prioridad, 
                   e.nombre AS especialidad, e.id_especialidad
            FROM sintoma s
            JOIN especialidad e ON e.id_especialidad = s.id_especialidad
            WHERE s.activo = 'S' AND e.activa = 'S'
            ORDER BY s.prioridad DESC, e.nombre, s.descripcion
            """
        )

    def buscar_especialidad_por_sintoma(self, sintoma: str) -> dict | None:
        return self.fetch_one(
            """
            SELECT s.id_sintoma, s.descripcion, s.prioridad,
                   e.id_especialidad, e.nombre AS especialidad
            FROM sintoma s
            JOIN especialidad e ON e.id_especialidad = s.id_especialidad
            WHERE UPPER(s.descripcion) LIKE '%' || UPPER(:sintoma) || '%'
              AND s.activo = 'S' AND e.activa = 'S'
            """,
            {"sintoma": sintoma},
        )

    def crear_sintoma(
        self, descripcion: str, id_especialidad: int, 
        prioridad: str = "MEDIA", activo: str = "S"
    ) -> int:
        return self.execute(
            """
            INSERT INTO sintoma (descripcion, id_especialidad, prioridad, activo)
            VALUES (:descripcion, :id_especialidad, :prioridad, :activo)
            """,
            {
                "descripcion": descripcion, "id_especialidad": id_especialidad,
                "prioridad": prioridad, "activo": activo,
            },
        )

    # ======================================================================
    # CONFIGURACION DEL HOSPITAL
    # ======================================================================

    def obtener_configuracion_hospital(self, id_configuracion: int = 1) -> dict | None:
        return self.fetch_one(
            """
            SELECT ch.id_configuracion, ch.nombre_hospital, ch.logo_url,
                   ch.color_primario, ch.color_secundario, ch.mensaje_bienvenida,
                   ch.requiere_derivacion, ch.tiempo_cancelacion_horas,
                   c.nombre AS centro_principal, c.direccion, c.telefono
            FROM configuracion_hospital ch
            JOIN centro_salud c ON c.id_centro = ch.id_centro_principal
            WHERE ch.id_configuracion = :id_configuracion
            """,
            {"id_configuracion": id_configuracion},
        )

    def crear_configuracion_hospital(
        self, nombre_hospital: str, id_centro_principal: int,
        logo_url: str | None = None, color_primario: str = "#0066cc",
        color_secundario: str = "#ffffff", mensaje_bienvenida: str | None = None,
        requiere_derivacion: str = "N", tiempo_cancelacion_horas: int = 24
    ) -> int:
        return self.execute(
            """
            INSERT INTO configuracion_hospital
              (nombre_hospital, id_centro_principal, logo_url, color_primario,
               color_secundario, mensaje_bienvenida, requiere_derivacion, tiempo_cancelacion_horas)
            VALUES
              (:nombre_hospital, :id_centro_principal, :logo_url, :color_primario,
               :color_secundario, :mensaje_bienvenida, :requiere_derivacion, :tiempo_cancelacion_horas)
            """,
            {
                "nombre_hospital": nombre_hospital, "id_centro_principal": id_centro_principal,
                "logo_url": logo_url, "color_primario": color_primario,
                "color_secundario": color_secundario, "mensaje_bienvenida": mensaje_bienvenida,
                "requiere_derivacion": requiere_derivacion, "tiempo_cancelacion_horas": tiempo_cancelacion_horas,
            },
        )

    # ======================================================================
    # TIPOS DE CONSULTA Y PRECIOS
    # ======================================================================

    def listar_tipos_consulta(self) -> list[dict]:
        return self.fetch_all(
            """
            SELECT id_tipo_consulta, nombre, descripcion, duracion_minutos, activo
            FROM tipo_consulta
            WHERE activo = 'S'
            ORDER BY nombre
            """
        )

    def obtener_precios_por_especialidad(
        self, id_centro: int, id_especialidad: int
    ) -> list[dict]:
        return self.fetch_all(
            """
            SELECT pe.id_precio, pe.precio_minimo, pe.precio_maximo, pe.precio_estimado,
                   tc.nombre AS tipo_consulta, tc.descripcion, tc.duracion_minutos
            FROM precio_especialidad pe
            JOIN tipo_consulta tc ON tc.id_tipo_consulta = pe.id_tipo_consulta
            WHERE pe.id_centro = :id_centro 
              AND pe.id_especialidad = :id_especialidad
              AND pe.activo = 'S' AND tc.activo = 'S'
            ORDER BY tc.nombre
            """,
            {"id_centro": id_centro, "id_especialidad": id_especialidad},
        )

    def obtener_precio_estimado_por_tipo(
        self, id_centro: int, id_especialidad: int, id_tipo_consulta: int
    ) -> dict | None:
        return self.fetch_one(
            """
            SELECT precio_minimo, precio_maximo, precio_estimado
            FROM precio_especialidad
            WHERE id_centro = :id_centro 
              AND id_especialidad = :id_especialidad
              AND id_tipo_consulta = :id_tipo_consulta
              AND activo = 'S'
            """,
            {
                "id_centro": id_centro, "id_especialidad": id_especialidad,
                "id_tipo_consulta": id_tipo_consulta,
            },
        )

    # ======================================================================
    # DISPONIBILIDAD DE TURNOS (MEJORADA)
    # ======================================================================

    def obtener_turnos_disponibles_por_medico(
        self, id_medico: int, dias: int = 7
    ) -> list[dict]:
        return self.fetch_all(
            """
            WITH fechas_disponibles AS (
                SELECT TRUNC(SYSDATE) + LEVEL AS fecha
                FROM dual
                CONNECT BY LEVEL <= :dias
            ),
            slots_agenda AS (
                SELECT fd.fecha,
                       a.dia_semana,
                       a.hora_inicio,
                       a.hora_fin,
                       a.duracion_minutos,
                       a.cupo_diario
                FROM fechas_disponibles fd
                JOIN agenda_medico a ON 
                    TO_CHAR(fd.fecha, 'DY', 'NLS_DATE_LANGUAGE=SPANISH') = a.dia_semana
                WHERE a.id_medico = :id_medico
            )
            SELECT sa.fecha,
                   sa.dia_semana,
                   sa.hora_inicio,
                   sa.hora_fin,
                   sa.duracion_minutos,
                   sa.cupo_diario,
                   sa.cupo_diario - COUNT(t.id_turno) AS cupos_disponibles
            FROM slots_agenda sa
            LEFT JOIN turno t ON 
                t.id_medico = :id_medico
                AND TRUNC(t.fecha_turno) = sa.fecha
                AND t.estado IN ('PENDIENTE', 'CONFIRMADO')
            GROUP BY sa.fecha, sa.dia_semana, sa.hora_inicio, sa.hora_fin,
                     sa.duracion_minutos, sa.cupo_diario
            HAVING sa.cupo_diario - COUNT(t.id_turno) > 0
            ORDER BY sa.fecha, sa.hora_inicio
            """,
            {"id_medico": id_medico, "dias": dias},
        )

    def obtener_medicos_disponibles_por_especialidad(
        self, id_centro: int, id_especialidad: int, dias: int = 7
    ) -> list[dict]:
        return self.fetch_all(
            """
            SELECT DISTINCT m.id_medico, m.nombre, m.matricula, m.telefono, m.email,
                   e.nombre AS especialidad
            FROM medico m
            JOIN especialidad e ON e.id_especialidad = m.id_especialidad
            JOIN agenda_medico a ON a.id_medico = m.id_medico
            WHERE m.id_centro = :id_centro
              AND m.id_especialidad = :id_especialidad
              AND m.activo = 'S'
              AND e.activa = 'S'
            ORDER BY m.nombre
            """,
            {"id_centro": id_centro, "id_especialidad": id_especialidad},
        )

    def obtener_horarios_disponibles(
        self, id_medico: int, fecha: str
    ) -> list[dict]:
        return self.fetch_all(
            """
            WITH slots AS (
                SELECT TO_DATE(:fecha || ' ' || a.hora_inicio, 'YYYY-MM-DD HH24:MI') + 
                       (LEVEL - 1) * (a.duracion_minutos / 1440) AS slot_inicio,
                       TO_DATE(:fecha || ' ' || a.hora_inicio, 'YYYY-MM-DD HH24:MI') + 
                       LEVEL * (a.duracion_minutos / 1440) AS slot_fin
                FROM agenda_medico a
                CROSS JOIN (
                    SELECT LEVEL FROM dual 
                    CONNECT BY LEVEL <= (a.cupo_diario)
                )
                WHERE a.id_medico = :id_medico
                  AND TO_CHAR(TO_DATE(:fecha, 'YYYY-MM-DD'), 'DY', 'NLS_DATE_LANGUAGE=SPANISH') = a.dia_semana
            )
            SELECT TO_CHAR(s.slot_inicio, 'HH24:MI') AS hora,
                   TO_CHAR(s.slot_fin, 'HH24:MI') AS hora_fin,
                   s.slot_inicio AS fecha_hora
            FROM slots s
            WHERE NOT EXISTS (
                SELECT 1 FROM turno t
                WHERE t.id_medico = :id_medico
                  AND t.fecha_turno BETWEEN s.slot_inicio AND s.slot_fin
                  AND t.estado IN ('PENDIENTE', 'CONFIRMADO')
            )
            ORDER BY s.slot_inicio
            """,
            {"id_medico": id_medico, "fecha": fecha},
        )

    # ======================================================================
    # CIERRE
    # ======================================================================

    def cerrar(self):
        """Cerrar conexion (placeholder para compatibilidad)."""
        pass


# ============================================================================
# Funcion de conveniencia para uso rapido
# ============================================================================

def crear_dao() -> SaludDAO:
    """Crear y retornar una instancia del DAO."""
    return SaludDAO()
