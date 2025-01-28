import pytest
import logging

from typing import Optional
from broker import KafkaWrapper

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka.schema_registry import SchemaRegistryClient, Schema
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

logger = logging.getLogger(__name__)

admin_client = AdminClient({"bootstrap.servers": "localhost:29092"})
sc_client = SchemaRegistryClient({"url": "http://localhost:8085"})
consumer = Consumer({"bootstrap.servers": "localhost:29092",
                     "group.id": "testGroup",
                     "auto.offset.reset": "earliest"})

TOPIC_NAME = "testTopic"
SUBJECT_NAME = "testSchema"
SCHEMA_PATH = "../json_schemas/test_schema.json"


class TestKafkaProducer:
    schema_id: Optional[int] = None

    @classmethod
    def setup_class(cls) -> None:
        logger.info("setting up test...")

        raw_schema = cls.open_schema(SCHEMA_PATH)
        schema_instance = Schema(schema_str=raw_schema, schema_type="JSON")

        try:
            cls.schema_id = sc_client.register_schema(subject_name=SUBJECT_NAME, schema=schema_instance)
            logger.info(f"register schema to schema registry with schema_id: {cls.schema_id}")
        except Exception as e:
            pytest.fail(f"failed register schema to schema registry with exception: {e}")

        fs = admin_client.create_topics([NewTopic(topic=TOPIC_NAME, num_partitions=3, replication_factor=1)])

        for topic, f in fs.items():
            try:
                f.result()
                logger.info(f"topic {topic} created")
            except Exception as e:
                pytest.fail(f"failed to create topic {topic}: {e}")

    @pytest.fixture(scope="class")
    def kafka_client(self) -> KafkaWrapper:
        return KafkaWrapper({"bootstrap.servers": "localhost:29092",
                             "schema.registry.url": "http://localhost:8085"})

    def test_produce(self, kafka_client: KafkaWrapper) -> None:
        test_schema = sc_client.get_schema(self.schema_id).schema_str
        test_value = {"id": 1, "description": "test"}

        kafka_client.produce(topic=TOPIC_NAME, value=test_value, subject_name=SUBJECT_NAME)

        consumer.subscribe([TOPIC_NAME])

        msg = consumer.poll(10.0)
        consumer.close()

        json_deserializer = JSONDeserializer(test_schema)
        decoded_message = json_deserializer(msg.value(), SerializationContext(TOPIC_NAME, MessageField.VALUE))

        assert decoded_message["id"] == 1
        assert decoded_message["description"] == "test"

    @classmethod
    def teardown_class(cls) -> None:
        logger.info("teardown...")

        try:
            versions = sc_client.delete_subject(SUBJECT_NAME)
            logger.info(f"delete versions from schema registry: {versions}")
        except Exception as e:
            pytest.fail(f"failed to delete subject in schema registry with exception: {e}")

        fs = admin_client.delete_topics([TOPIC_NAME], operation_timeout=30)

        for topic, f in fs.items():
            try:
                f.result()
                logger.info(f"topic {topic} deleted")
            except Exception as e:
                pytest.fail(f"failed to delete topic {topic}: {e}")

    @staticmethod
    def open_schema(path):
        with open(path) as data:
            raw_schema = data.read()
        return raw_schema
