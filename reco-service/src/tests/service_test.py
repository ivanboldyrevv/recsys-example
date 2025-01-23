import pytest
import psycopg2

from peewee import PostgresqlDatabase
from models import ItemModel

from service import Service
from kv_storage import KeyValueStorage
from broker import BrokerClient

from transport.request import Item, UserItemSequence


class RedisMock(KeyValueStorage):
    """
        This is mock for redis storage.
        Method get() returns a list consisting of two
        encoded uid's cause' original get() method returns encoded str.
    """
    def set(self):
        pass

    def get(self, user_id: str):
        return ["id_1".encode(), "id_2".encode()]

    def delete(self, user_id: str):
        pass


class KafkaMock(BrokerClient):
    def produce(self, topic, value, schema):
        return super().produce(topic, value, schema)


class TestService:

    models = [ItemModel]
    test_db = None

    @classmethod
    def setup_class(cls):
        default_connection = {
            "database": "test",
            "host": "localhost",
            "port": 5430,
            "user": "postgres_user",
            "password": "postgres_password"
        }

        try:
            connection = psycopg2.connect(**default_connection)
            connection.close()
        except psycopg2.errors.OperationalError:
            not_default = default_connection.copy()
            not_default["database"] = "postgres"

            connection = psycopg2.connect(**not_default)
            connection.autocommit = True
            cursor = connection.cursor()

            cursor.execute("create database test")

            connection.close()
            raise Exception("The test database has been initialized. Run the tests again!")

        cls.test_db = PostgresqlDatabase(**default_connection)
        cls.test_db.bind(cls.models, bind_refs=False, bind_backrefs=False)
        cls.test_db.connect()
        cls.test_db.create_tables(cls.models)

    @pytest.fixture(scope="class")
    def service(request):
        class MockedService(Service):
            def read_schema_from_file(self, path: str) -> None:
                return

        mock_kafka = KafkaMock()
        mock_redis = RedisMock()

        service = MockedService(mock_kafka, mock_redis)

        return service

    def test_fetch_items(self, service: Service):
        data_source = self.data_source()

        ItemModel.insert_many(data_source).execute()
        items = service.fetch_items()

        for idx, item in enumerate(items):
            assert item.iid == data_source[idx]["item_id"]
            assert item.description == data_source[idx]["description"]
            assert item.image_url == data_source[idx]["image_url"]

    def test_fetch_recommendation(self, service: Service):
        data_source = self.data_source()
        item_sequence = UserItemSequence(uid="t-uid-est", item_sequence=[Item(iid="test-iid", description="test-desc")])

        recommendations = service.fetch_recommendations(item_sequence).recommendations
        for idx, item in enumerate(recommendations):
            assert item.iid == data_source[idx]["item_id"]
            assert item.description == data_source[idx]["description"]
            assert item.image_url == data_source[idx]["image_url"]

    @staticmethod
    def data_source():
        return [
            {"item_id": "id_1", "description": "desc_1", "image_url": "http://test_image_1.su"},
            {"item_id": "id_2", "description": "desc_2", "image_url": "http://test_image_2.su"}
        ]

    @classmethod
    def teardown_class(cls):
        cls.test_db.drop_tables(TestService.models)
        cls.test_db.close()
