#!/usr/bin/env python3
"""Creating a redis cache class"""
import redis
from typing import Union, Optional, Callable, Any
import uuid
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Wrapper function that counts number of times methods called"""
    key: str = method.__qualname__

    @wraps(method)
    def increment_calls(self, *args: Any, **kwargs: Any) -> Any:
        """Increment the calls method"""
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return increment_calls


def call_history(method: Callable) -> Callable:
    """Stores the history of inputs and outputs for a method"""
    @wraps(method)
    def store_history(self, *args: Any, **kwargs: Any) -> Any:
        """Stores the history of inputs and outputs for a method"""
        input_key: str = str(method.__qualname__) + ":inputs"
        self._redis.rpush(input_key, str(args))

        output_key: str = str(method.__qualname__) + ":outputs"
        output: Any = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        return output
    return store_history


def replay(methos: Callable) -> None:
    """Displays the history of calls of a method"""
    redis_instance = redis.Redis()
    meth: str = methos.__qualname__
    inputs_key: str = meth + ":inputs"
    outputs_key: str = meth + ":outputs"

    inputs = redis_instance.lrange(inputs_key, 0, -1)
    outputs = redis_instance.lrange(outputs_key, 0, -1)

    print(f"{meth} was called {len(inputs)} times:")

    for i, (input, out) in enumerate(zip(inputs, outputs)):
        print(f"{meth}(*{input.decode('utf-8')}) -> {out.decode('utf-8')}")


class Cache:
    """Redis class that stores instance of the redis client"""
    def __init__(self) -> None:
        """The init method"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
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
