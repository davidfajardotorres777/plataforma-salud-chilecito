import re
from typing import Any

from src.config.database import OracleDatabase


class BaseDAO:
    table_name = ""

    def __init__(self, db: OracleDatabase | None = None):
        self.db = db or OracleDatabase()

    def fetch_all(self, sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.db.fetch_all(sql, params)

    def fetch_one(self, sql: str, params: dict[str, Any] | None = None) -> dict[str, Any] | None:
        return self.db.fetch_one(sql, params)

    def execute(self, sql: str, params: dict[str, Any] | list[dict[str, Any]] | None = None) -> int:
        return self.db.execute(sql, params)

    def contar(self) -> int:
        if not re.match(r"^[a-zA-Z0-9_]+$", self.table_name):
            raise ValueError(f"Invalid table name: {self.table_name}")
        row = self.fetch_one(f"SELECT COUNT(*) AS total FROM {self.table_name}")
        return int(row["total"]) if row else 0
