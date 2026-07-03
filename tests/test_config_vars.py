import os
from unittest.mock import patch
from config_vars import get_app_config

@patch("config_vars.load_dotenv")
def test_get_app_config_defaults(mock_load_dotenv):
    """Test get_app_config returns default values when environment variables are missing."""
    with patch.dict(os.environ, {}, clear=True):
        config = get_app_config()

        # Verify load_dotenv was called (if it's not None)
        if mock_load_dotenv is not None:
            mock_load_dotenv.assert_called_once()

        assert config == {
            "secret_key": "tu-clave-secreta-aqui-cambiala-en-produccion",
            "base_url": "http://localhost:8000",
            "environment": "development",
        }

@patch("config_vars.load_dotenv")
def test_get_app_config_custom_env_vars(mock_load_dotenv):
    """Test get_app_config returns custom values from environment variables."""
    custom_env = {
        "SECRET_KEY": "my-super-secret-key",
        "BASE_URL": "https://api.production.com",
        "ENVIRONMENT": "production",
    }
    with patch.dict(os.environ, custom_env, clear=True):
        config = get_app_config()

        # Verify load_dotenv was called (if it's not None)
        if mock_load_dotenv is not None:
            mock_load_dotenv.assert_called_once()

        assert config == {
            "secret_key": "my-super-secret-key",
            "base_url": "https://api.production.com",
            "environment": "production",
        }
