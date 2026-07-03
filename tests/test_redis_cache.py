import pytest
import json
from unittest.mock import patch, MagicMock
from redis_cache import RedisCache

@pytest.fixture
def mock_redis_config():
    with patch("redis_cache.get_redis_config") as mock:
        mock.return_value = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": None
        }
        yield mock

@pytest.fixture
def mock_redis():
    with patch("redis.Redis") as mock:
        yield mock

def test_init(mock_redis_config):
    cache = RedisCache()
    assert cache._client is None
    assert cache._config == mock_redis_config.return_value

def test_get_client_without_password(mock_redis_config, mock_redis):
    cache = RedisCache()
    client = cache._get_client()

    mock_redis.assert_called_once_with(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )
    assert client == mock_redis.return_value
    assert cache._client == client

    # Second call should not recreate
    mock_redis.reset_mock()
    client2 = cache._get_client()
    assert client2 == client
    mock_redis.assert_not_called()

def test_get_client_with_password():
    with patch("redis_cache.get_redis_config") as mock_config:
        mock_config.return_value = {
            "host": "localhost",
            "port": 6379,
            "db": 0,
            "password": "secret_password"
        }

        with patch("redis.Redis") as mock_redis:
            cache = RedisCache()
            cache._get_client()

            mock_redis.assert_called_once_with(
                host="localhost",
                port=6379,
                db=0,
                password="secret_password",
                decode_responses=True
            )

def test_ping_ok(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_redis.return_value = mock_client

    assert cache.ping() == "OK"
    mock_client.ping.assert_called_once()

def test_ping_fail(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.ping.side_effect = Exception("Connection error")
    mock_redis.return_value = mock_client

    assert cache.ping() == "SIN_RESPUESTA"

def test_set_with_ttl(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.setex.return_value = True
    mock_redis.return_value = mock_client

    data = {"key": "value"}
    result = cache.set("test_key", data, ttl=3600)

    assert result is True
    mock_client.setex.assert_called_once_with(
        "test_key",
        3600,
        json.dumps(data)
    )

def test_set_without_ttl(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.set.return_value = True
    mock_redis.return_value = mock_client

    data = {"key": "value"}
    result = cache.set("test_key", data)

    assert result is True
    mock_client.set.assert_called_once_with(
        "test_key",
        json.dumps(data)
    )

def test_set_exception(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.set.side_effect = Exception("Redis error")
    mock_redis.return_value = mock_client

    assert cache.set("test_key", "value") is False

def test_get_exists(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    data = {"key": "value"}
    mock_client.get.return_value = json.dumps(data)
    mock_redis.return_value = mock_client

    result = cache.get("test_key")

    assert result == data
    mock_client.get.assert_called_once_with("test_key")

def test_get_not_exists(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.get.return_value = None
    mock_redis.return_value = mock_client

    result = cache.get("test_key")

    assert result is None

def test_get_exception(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.get.side_effect = Exception("Redis error")
    mock_redis.return_value = mock_client

    assert cache.get("test_key") is None

def test_delete(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.delete.return_value = 1
    mock_redis.return_value = mock_client

    assert cache.delete("test_key") is True
    mock_client.delete.assert_called_once_with("test_key")

def test_delete_exception(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.delete.side_effect = Exception("Redis error")
    mock_redis.return_value = mock_client

    assert cache.delete("test_key") is False

def test_exists(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.exists.return_value = 1
    mock_redis.return_value = mock_client

    assert cache.exists("test_key") is True
    mock_client.exists.assert_called_once_with("test_key")

def test_exists_exception(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.exists.side_effect = Exception("Redis error")
    mock_redis.return_value = mock_client

    assert cache.exists("test_key") is False

def test_set_session(mock_redis_config):
    cache = RedisCache()
    with patch.object(cache, 'set') as mock_set:
        mock_set.return_value = True

        data = {"user": "test"}
        result = cache.set_session("123", data, ttl=1000)

        assert result is True
        mock_set.assert_called_once_with("session:123", data, 1000)

def test_get_session(mock_redis_config):
    cache = RedisCache()
    with patch.object(cache, 'get') as mock_get:
        expected = {"user": "test"}
        mock_get.return_value = expected

        result = cache.get_session("123")

        assert result == expected
        mock_get.assert_called_once_with("session:123")

def test_delete_session(mock_redis_config):
    cache = RedisCache()
    with patch.object(cache, 'delete') as mock_delete:
        mock_delete.return_value = True

        result = cache.delete_session("123")

        assert result is True
        mock_delete.assert_called_once_with("session:123")

def test_invalidate_user_sessions(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()

    # Mock keys matching session pattern
    mock_client.keys.return_value = ["session:1", "session:2", "session:3"]

    # Mock deletes
    mock_client.delete.return_value = 1
    mock_redis.return_value = mock_client

    with patch.object(cache, 'get') as mock_get:
        # Session 1 belongs to user_id 'u1'
        # Session 2 belongs to user_id 'u2'
        # Session 3 is None (doesn't exist anymore/expired just now)
        def mock_get_side_effect(key):
            if key == "1": return {"usuario_id": "u1"}
            if key == "2": return {"usuario_id": "u2"}
            if key == "3": return None

        mock_get.side_effect = mock_get_side_effect

        # Invalidate for user 'u1'
        result = cache.invalidate_user_sessions("u1")

        assert result is True
        mock_client.keys.assert_called_once_with("session:*")

        # Should only delete "session:1"
        mock_client.delete.assert_called_once_with("session:1")

def test_invalidate_user_sessions_exception(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.keys.side_effect = Exception("Redis error")
    mock_redis.return_value = mock_client

    assert cache.invalidate_user_sessions("u1") is False

def test_clear_all(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_redis.return_value = mock_client

    assert cache.clear_all() is True
    mock_client.flushdb.assert_called_once()

def test_clear_all_exception(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_client.flushdb.side_effect = Exception("Redis error")
    mock_redis.return_value = mock_client

    assert cache.clear_all() is False

def test_cerrar(mock_redis_config, mock_redis):
    cache = RedisCache()
    mock_client = MagicMock()
    mock_redis.return_value = mock_client

    # Ensure client is populated
    cache._get_client()
    assert cache._client is not None

    cache.cerrar()

    mock_client.close.assert_called_once()
    assert cache._client is None

def test_cerrar_no_client(mock_redis_config):
    cache = RedisCache()
    # Client is None initially
    cache.cerrar() # Should not raise error
