from uuid import uuid4
from typing import Dict, Any
from abc import ABC, abstractmethod

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer


class BrokerClient(ABC):
    """
        Интерфейс для определения работы брокера.
    """

    @abstractmethod
    def produce(self, topic: str, value: Dict[str, Any], schema: str) -> None:
        pass


class KafkaWrapper(BrokerClient):
    def __init__(self, config: Dict[str, str]):
        """
            Interface of an object that is designed
            to pass messages to a Kafka topic.
            Takes the schema by subject_name, serializes
            the data and passes it to the topic.

            config (* indicates a required field):
                bootstrap.servers*: str = kafka host:port
                schema.registry.url*: str = schema registry http://host:port
        """
        self.config = config

    def produce(self, topic: str, value: Dict[str, Any], subject_name: str) -> None:
        sc_client = SchemaRegistryClient({"url": self.config["schema.registry.url"]})
        latest_ver = sc_client.get_versions(subject_name)[-1]
        response = sc_client.get_version(subject_name, latest_ver)

        schema = response.schema

        string_serializer = StringSerializer()
        json_serializer = JSONSerializer(schema.schema_str, sc_client)

        producer = Producer({"bootstrap.servers": self.config["bootstrap.servers"]})

        try:
            producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             value=json_serializer(value, SerializationContext(topic, MessageField.VALUE)),
                             on_delivery=self.delivery_report)
        except Exception as e:
            print(e)

        print("\nFlushing records...")
        producer.flush()

    def delivery_report(self, err, msg):
        """
        Reports the success or failure of a message delivery.

        args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.
        """

        if err is not None:
            print("Delivery failed for User record {}: {}".format(msg.key(), err))
            return
        print('User record {} successfully produced to {} [{}] at offset {}'.format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()))
