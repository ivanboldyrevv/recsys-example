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
    def __init__(self, conf):
        self.conf = conf
        self.client = redis.Redis(**self.conf)

    def set(self, key, value):
        with self.client.pipeline() as pipe:
            pipe.delete(key)
            pipe.lpush(key, *value)
            pipe.execute()

    def get(self, key):
        """fetch all items"""
        return self.client.lrange(key, 0, -1)

    def delete(self, key):
        return self.client.delete(key)
