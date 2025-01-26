from kv_storage import KeyValueStorage
from broker import BrokerClient


class KeyValueStorageMock(KeyValueStorage):
    def set(self):
        pass

    def get(self, *args, **kwargs):
        return ["id_1".encode(), "id_2".encode()]

    def delete(self, user_id: str):
        pass


class BrokerMock(BrokerClient):
    def produce(self, *args, **kwargs):
        return "produced :)"
