import os
from unittest.mock import patch
import config_vars

def test_get_mongo_config_defaults():
    with patch.dict(os.environ, {}, clear=True):
        config = config_vars.get_mongo_config()
        assert config["uri"] == "mongodb://localhost:27017"
        assert config["db_name"] == "salud_chilecito"

def test_get_mongo_config_with_env():
    with patch.dict(os.environ, {"MONGO_URI": "mongodb://remote:27017", "DB_NAME": "test_db"}, clear=True):
        config = config_vars.get_mongo_config()
        assert config["uri"] == "mongodb://remote:27017"
        assert config["db_name"] == "test_db"

def test_get_redis_config_defaults():
    with patch.dict(os.environ, {}, clear=True):
        config = config_vars.get_redis_config()
        assert config["host"] == "localhost"
        assert config["port"] == 6379
        assert config["db"] == 0
        assert config["password"] is None

def test_get_redis_config_with_env():
    with patch.dict(os.environ, {"REDIS_HOST": "redis.server", "REDIS_PORT": "6380", "REDIS_DB": "1", "REDIS_PASSWORD": "secretpassword"}, clear=True):
        config = config_vars.get_redis_config()
        assert config["host"] == "redis.server"
        assert config["port"] == 6380
        assert config["db"] == 1
        assert config["password"] == "secretpassword"

def test_get_email_config_defaults():
    with patch.dict(os.environ, {}, clear=True):
        config = config_vars.get_email_config()
        assert config["smtp_server"] == "smtp.gmail.com"
        assert config["smtp_port"] == 587
        assert config["smtp_username"] == ""
        assert config["smtp_password"] == ""
        assert config["from_email"] == "noreply@saludchilecito.com"

def test_get_email_config_with_env():
    with patch.dict(os.environ, {"SMTP_SERVER": "smtp.test.com", "SMTP_PORT": "465", "SMTP_USERNAME": "test_user", "SMTP_PASSWORD": "test_password", "FROM_EMAIL": "test@test.com"}, clear=True):
        config = config_vars.get_email_config()
        assert config["smtp_server"] == "smtp.test.com"
        assert config["smtp_port"] == 465
        assert config["smtp_username"] == "test_user"
        assert config["smtp_password"] == "test_password"
        assert config["from_email"] == "test@test.com"

def test_get_app_config_defaults():
    with patch.dict(os.environ, {}, clear=True):
        config = config_vars.get_app_config()
        assert config["secret_key"] == "tu-clave-secreta-aqui-cambiala-en-produccion"
        assert config["base_url"] == "http://localhost:8000"
        assert config["environment"] == "development"

def test_get_app_config_with_env():
    with patch.dict(os.environ, {"SECRET_KEY": "supersecret", "BASE_URL": "https://api.test.com", "ENVIRONMENT": "production"}, clear=True):
        config = config_vars.get_app_config()
        assert config["secret_key"] == "supersecret"
        assert config["base_url"] == "https://api.test.com"
        assert config["environment"] == "production"

def test_dotenv_called_if_available():
    # If load_dotenv is not None, it should be called in each config function
    if config_vars.load_dotenv is not None:
        with patch('config_vars.load_dotenv') as mock_load_dotenv:
            config_vars.get_mongo_config()
            mock_load_dotenv.assert_called_once()

            mock_load_dotenv.reset_mock()
            config_vars.get_redis_config()
            mock_load_dotenv.assert_called_once()

            mock_load_dotenv.reset_mock()
            config_vars.get_email_config()
            mock_load_dotenv.assert_called_once()

            mock_load_dotenv.reset_mock()
            config_vars.get_app_config()
            mock_load_dotenv.assert_called_once()
