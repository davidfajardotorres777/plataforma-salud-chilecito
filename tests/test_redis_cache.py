import json
from unittest.mock import MagicMock, patch
import pytest
from redis_cache import RedisCache

def test_redis_cache_set():
    cache = RedisCache()
    mock_client = MagicMock()
    # The set method of the mock returns True, because redis client returns True or something truthy on success.
    # Let's set it to True here.
    mock_client.set.return_value = True
    mock_client.setex.return_value = True
    cache._get_client = MagicMock(return_value=mock_client)

    # Test setting a string value
    assert cache.set("my_key", "my_value") is True
    mock_client.set.assert_called_once_with("my_key", json.dumps("my_value"))

    mock_client.reset_mock()

    # Test setting a value with TTL
    assert cache.set("my_key", "my_value", ttl=3600) is True
    mock_client.setex.assert_called_once_with("my_key", 3600, json.dumps("my_value"))

    mock_client.reset_mock()

    # Test setting a complex dictionary
    test_dict = {"a": 1, "b": "two"}
    assert cache.set("dict_key", test_dict) is True
    mock_client.set.assert_called_once_with("dict_key", json.dumps(test_dict))

    mock_client.reset_mock()

    # Test exception handling
    mock_client.set.side_effect = Exception("Redis error")
    assert cache.set("error_key", "value") is False
