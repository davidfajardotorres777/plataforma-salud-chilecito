import pytest
from unittest.mock import patch
from redis_cache import RedisCache

def test_redis_cache_set_error():
    """Test que verifica que set retorna False cuando hay una excepción en Redis"""
    cache = RedisCache()

    with patch.object(cache, '_get_client') as mock_get_client:
        mock_get_client.side_effect = Exception("Error de conexión simulado")

        result = cache.set("test_key", "test_value")

        assert result is False
