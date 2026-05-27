from contextlib import contextmanager
from typing import Any, Iterable

from .settings import DatabaseSettings, get_settings


class OracleDatabase:
    """Small wrapper around python-oracledb for DAO classes."""

    def __init__(self, settings: DatabaseSettings | None = None):
        self.settings = settings or get_settings()
        self._thick_initialized = False

    def _load_driver(self):
        try:
            import oracledb
        except ImportError as exc:  # pragma: no cover - depends on local env
            raise RuntimeError(
                "Falta instalar python-oracledb. Ejecuta: pip install -r requirements.txt"
            ) from exc

        if self.settings.thick_mode and not self._thick_initialized:
            oracledb.init_oracle_client()
            self._thick_initialized = True

        return oracledb

    @contextmanager
    def connection(self):
        oracledb = self._load_driver()
        conn = oracledb.connect(
            user=self.settings.user,
            password=self.settings.password,
            dsn=self.settings.dsn,
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

    def execute(self, sql: str, params: dict[str, Any] | Iterable[dict[str, Any]] | None = None) -> int:
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
