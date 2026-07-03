import json
import pytest
from unittest.mock import MagicMock, patch
from redis_cache import RedisCache
from datetime import date

@pytest.fixture
def mock_redis_client():
    client = MagicMock()
    # Ensure set and setex return True as the real Redis client does when successful
    client.set.return_value = True
    client.setex.return_value = True
    return client

@pytest.fixture
def redis_cache(mock_redis_client):
    # Use patch to avoid loading real config or redis in __init__ if necessary,
    # but based on __init__ it just calls get_redis_config() which should be fine.
    # Actually let's patch get_redis_config just in case it fails in test environment without env vars.
    with patch('redis_cache.get_redis_config', return_value={'host': 'localhost', 'port': 6379, 'db': 0, 'password': None}):
        cache = RedisCache()

    # Mock the internal _get_client method to return our mock_redis_client
    cache._get_client = MagicMock(return_value=mock_redis_client)
    return cache

def test_set_without_ttl(redis_cache, mock_redis_client):
    key = "test_key"
    value = {"name": "Test", "value": 123}

    result = redis_cache.set(key, value)

    assert result is True
    redis_cache._get_client.assert_called_once()
    mock_redis_client.set.assert_called_once_with(key, json.dumps(value, default=str))
    mock_redis_client.setex.assert_not_called()

def test_set_with_ttl(redis_cache, mock_redis_client):
    key = "test_key_ttl"
    value = "simple_string"
    ttl = 3600

    result = redis_cache.set(key, value, ttl=ttl)

    assert result is True
    redis_cache._get_client.assert_called_once()
    mock_redis_client.setex.assert_called_once_with(key, ttl, json.dumps(value, default=str))
    mock_redis_client.set.assert_not_called()

def test_set_serialization_with_default(redis_cache, mock_redis_client):
    key = "test_date"
    # date object is not JSON serializable by default, so json.dumps(..., default=str) should be used
    value = {"date": date(2023, 1, 1)}

    result = redis_cache.set(key, value)

    assert result is True
    expected_serialized = json.dumps(value, default=str)
    mock_redis_client.set.assert_called_once_with(key, expected_serialized)

def test_set_handles_get_client_exception(redis_cache):
    # Mock _get_client to raise an exception
    redis_cache._get_client.side_effect = Exception("Connection error")

    result = redis_cache.set("key", "value")

    assert result is False

def test_set_handles_client_exception(redis_cache, mock_redis_client):
    # Mock the redis client's set method to raise an exception
    mock_redis_client.set.side_effect = Exception("Redis error")

    result = redis_cache.set("key", "value")

    assert result is False
