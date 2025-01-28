import logging
import pytest
import redis
from key_value import RedisClient

logger = logging.getLogger(__name__)

test_config = {"host": "localhost", "port": 6379, "db": 0}
test_client = redis.Redis(**test_config)

TEST_VALUES = ["value#1", "value#2"]


class TestRedisClient:

    @classmethod
    def setup_class(self):
        logger.info("start setup class...")
        test_client.flushdb()

    @pytest.fixture(scope="class")
    def redis_client(self) -> RedisClient:
        return RedisClient(test_config)

    def test_set(self, redis_client: RedisClient):
        redis_client.set("test", TEST_VALUES)

        returned_values = test_client.lrange("test", 0, -1)
        decoded_values = [i.decode() for i in returned_values]

        assert decoded_values == TEST_VALUES[::-1]

    def test_get(self, redis_client: RedisClient):
        returned_values = redis_client.get("test")
        assert returned_values == TEST_VALUES

    def test_delete(self, redis_client: RedisClient):
        redis_client.delete("test")
        returned_values = test_client.lrange("test", 0, -1)

        assert not returned_values

    @classmethod
    def teardown_class(self):
        logger.info("teardown class...")
        test_client.flushdb()
