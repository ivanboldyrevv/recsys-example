import logging

from uuid import uuid4
from typing import Dict, Any
from abc import ABC, abstractmethod

from confluent_kafka import Producer, KafkaError, Message as KafkaMessage
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer


logger = logging.getLogger(__name__)


class BrokerClient(ABC):
    """
        An interface that must be implemented by objects
        that are broker producers.
    """

    @abstractmethod
    def produce(self, topic: str, value: Dict[str, Any], subject_name: str) -> None:
        pass


class KafkaRelay(BrokerClient):
    def __init__(self, config: Dict[str, str]):
        """
            Interface of an object that is designed
            to produce messages to a Kafka topic.
            Takes the schema by subject_name, serializes
            the data and passes it to the topic.

            config (* indicates a required field):
                bootstrap.servers*: str = kafka host:port
                schema.registry.url*: str = schema registry http://host:port
        """
        self.config = config

    def produce(self, topic: str, value: Dict[str, Any], subject_name: str) -> None:
        """
            Takes the schema from the registry schema.
            Serializes the message in accordance with
            the scheme and sends it to the topic

            args:
                topic: str = kafka topic
                value: dict[str, str] = message value
                subject_name: str = schema subject name in schema registry
        """
        schema = self.fetch_schema(subject_name=subject_name)

        string_serializer = StringSerializer()
        json_serializer = JSONSerializer(schema.schema_str, self.fetch_schema_registry())

        producer = Producer({"bootstrap.servers": self.config["bootstrap.servers"]})

        try:
            producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             value=json_serializer(value, SerializationContext(topic, MessageField.VALUE)),
                             on_delivery=self.delivery_report)
        except Exception as e:
            logger.warning(f"exception occured: {e}")

        producer.flush()

    def fetch_schema(self, subject_name: str):
        schema_registry = self.fetch_schema_registry()
        latest_ver = schema_registry.get_versions(subject_name)[-1]
        return schema_registry.get_version(subject_name, latest_ver).schema

    def fetch_schema_registry(self):
        return SchemaRegistryClient({"url": self.config["schema.registry.url"]})

    def delivery_report(self, err: KafkaError, msg: KafkaMessage) -> None:
        if err is not None:
            logger.warning("Delivery failed for User record {}: {}".format(msg.key(), err))
            return
        logger.info(f"User record {msg.key()} successfully produced"
                    f"to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
