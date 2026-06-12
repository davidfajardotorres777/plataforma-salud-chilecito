import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def get_mongo_config():
    """ Retorna las variables de conexión a MongoDB desde .env """
    if load_dotenv is not None:
        load_dotenv()

    return {
        "uri": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
        "db_name": os.getenv("DB_NAME", "salud_chilecito"),
    }


def get_redis_config():
    """ Retorna las variables de conexión a Redis desde .env """
    if load_dotenv is not None:
        load_dotenv()

    return {
        "host": os.getenv("REDIS_HOST", "localhost"),
        "port": int(os.getenv("REDIS_PORT", "6379")),
        "db": int(os.getenv("REDIS_DB", "0")),
        "password": os.getenv("REDIS_PASSWORD", None),
    }


def get_email_config():
    """ Retorna las variables de configuración para envío de emails desde .env """
    if load_dotenv is not None:
        load_dotenv()

    return {
        "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", "587")),
        "smtp_username": os.getenv("SMTP_USERNAME", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "from_email": os.getenv("FROM_EMAIL", "noreply@saludchilecito.com"),
    }


def get_app_config():
    """ Retorna las variables de configuración de la aplicación desde .env """
    if load_dotenv is not None:
        load_dotenv()

    return {
        "secret_key": os.getenv("SECRET_KEY", "tu-clave-secreta-aqui-cambiala-en-produccion"),
        "base_url": os.getenv("BASE_URL", "http://localhost:8000"),
        "environment": os.getenv("ENVIRONMENT", "development"),
    }
