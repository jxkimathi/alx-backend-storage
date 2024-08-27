#!/usr/bin/env python3
"""Creating a redis cache class"""
import redis
from typing import Union, Optional, Callable, Any
import uuid


class Cache:
    """Redis class that stores instance of the redis client"""
    def __init__(self) -> None:
        """The init method"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores data in the redis instance"""
        key: str = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
            self,
            key: str,
            fn: Optional[Callable[[bytes], Any]] = None) -> Optional[Any]:
        """Get data from Redis instance"""
        value: Optional[bytes] = self._redis.get(key)
        if not value:
            return None

        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """Get data from redis instance"""
        return self.get(key, str)

    def get_int(self, key: str) -> Optional[int]:
        """Get data from redis instance as int"""
        return self.get(key, int)
