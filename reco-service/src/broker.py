from uuid import uuid4
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

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
        ...


class RabbitWrapper(BrokerClient):
    def __init__(self) -> None:
        pass

    def produce(self, topic: str, value: Dict[str, Any], schema: str) -> None:
        pass


@dataclass
class KafkaWrapperConfig:
    """
        Kafka producer config + schema registry config.
        Kafka client config params: https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
        Schema registry client cfg_params: ->
            ->https://docs.confluent.io/platform/current/clients/confluent-kafka-python/html/index.html#schemaregistryclient
        + schema_path
    """

    bootstrap_server: str
    schema_registry_url: str
    # security_protocol: str = "PLAINTEXT"
    ssl_ca_location: Optional[str] = None
    ssl_certificate_location: Optional[str] = None
    ssl_key_location: Optional[str] = None
    ssl_key_password: Optional[str] = None

    basic_auth_user_info: Optional[str] = None
    basic_auth_credentials_source: Optional[str] = None

    schema: Optional[str] = None
    schema_subject_name_strategy: Optional[str] = None


class KafkaWrapper(BrokerClient):
    def __init__(self, config: KafkaWrapperConfig):
        self.config = config

    def produce(self, topic: str, value: Dict[str, Any], schema: str) -> None:
        string_serializer = StringSerializer()
        schema_registry_client = SchemaRegistryClient({"url": self.config.schema_registry_url})
        json_serializer = JSONSerializer(schema, schema_registry_client)

        producer = Producer({"bootstrap.servers": self.config.bootstrap_server})

        try:
            producer.produce(
                topic=topic,
                key=string_serializer(str(uuid4())),
                value=json_serializer(value, SerializationContext(topic, MessageField.VALUE)),
                on_delivery=self.delivery_report)
        except Exception as e:
            print(e)

        print("\nFlushing records...")
        producer.flush()

    def _to_dict(self, value) -> Dict[str, Any]:
        """
            Serialize pydantic object to dict.
            args:
                value: pydantic obj
            return: Dict[Any]
        """
        return value.to_dict()

    def delivery_report(self, err, msg):
        """
        Reports the success or failure of a message delivery.

        Args:
            err (KafkaError): The error that occurred on None on success.
            msg (Message): The message that was produced or failed.
        """

        if err is not None:
            print("Delivery failed for User record {}: {}".format(msg.key(), err))
            return
        print('User record {} successfully produced to {} [{}] at offset {}'.format(
            msg.key(), msg.topic(), msg.partition(), msg.offset()))
