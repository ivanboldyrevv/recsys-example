from abc import ABC, abstractmethod
import redis


class KeyValueStorage(ABC):

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def delete(self, key):
        pass


class MemcachedStorage(KeyValueStorage):
    pass


class RedisStorage(KeyValueStorage):
    def __init__(self, host, port, db):
        self.client = redis.Redis(host=host, port=port, db=db)

    def set(self, key, value):
        return self.client.set(key, value)

    def get(self, key):
        """fetch all items"""
        return self.client.lrange(key, 0, -1)

    def delete(self, key):
        return self.client.delete(key)
