import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def get_db_config():
    """ Retorna las variables de conexion a Oracle desde .env """
    if load_dotenv is not None:
        load_dotenv()

    return {
        "user": os.getenv("DB_USER", "salud"),
        "password": os.getenv("DB_PASSWORD", "salud123"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "1521")),
        "service": os.getenv("DB_SERVICE", "XEPDB1"),
    }
