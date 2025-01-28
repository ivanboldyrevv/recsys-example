from typing import Dict, List, Any
from abc import ABC, abstractmethod
import redis


class Storage(ABC):
    """
        An interface that parent key-value database
        classes must implement.
    """

    @abstractmethod
    def set(self, key: str, value: List[Any]) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass


class RedisClient(Storage):
    def __init__(self, config: Dict[str, str]) -> None:
        """
            redis wrapper.

            config (* indicates a required field):
                host*: str = redis host
                port*: int = redis port
                and other unecessary redis args
        """
        self.r = redis.Redis(**config)

    def set(self, key: str, value: List[Any]) -> int:
        return self.r.lpush(key, *value)

    def get(self, key: str) -> List[str]:
        values = self.r.lrange(key, 0, -1)
        decoded = [i.decode() for i in values[::-1]]
        return decoded

    def delete(self, key: str) -> int:
        return self.r.delete(key)
