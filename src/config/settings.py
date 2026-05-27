from dataclasses import dataclass
import os

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional during static tests
    load_dotenv = None


@dataclass(frozen=True)
class DatabaseSettings:
    user: str
    password: str
    host: str
    port: int
    service: str
    thick_mode: bool = False

    @property
    def dsn(self) -> str:
        return f"{self.host}:{self.port}/{self.service}"


def get_settings() -> DatabaseSettings:
    if load_dotenv is not None:
        load_dotenv()

    return DatabaseSettings(
        user=os.getenv("DB_USER", "salud"),
        password=os.getenv("DB_PASSWORD", "salud123"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "1521")),
        service=os.getenv("DB_SERVICE", "XEPDB1"),
        thick_mode=os.getenv("DB_THICK_MODE", "false").lower() == "true",
    )
