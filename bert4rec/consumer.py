from builder import RecommendationBuilder
from recbole.quick_start import load_data_and_model

from dataclasses import dataclass, field
from typing import List

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer

import redis


r = redis.Redis(host="localhost", port=6379, db=0)

config, model, dataset, *_ = load_data_and_model(
    model_file="./saved/BERT4Rec-Dec-17-2024_15-29-26.pth"
)

r_handler = RecommendationBuilder(dataset, model)


@dataclass
class Item:
    iid: str
    description: str


@dataclass
class UserItemSequence:
    uid: str
    item_sequence: List[Item] = field(default_factory=list)


def to_dict(obj, ctx):
    if obj is None:
        return None

    sequence = UserItemSequence(
        uid=obj["uid"],
        item_sequence=[Item(item["iid"], item["description"]) for item in obj["item_sequence"]]
    )

    return sequence


def main(**kwargs):
    topic = kwargs["topic"]

    schema_str = """
    {
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "user-item-sequence",
      "type": "object",
      "properties": {
        "uid": {"type": "string"},
        "item_sequence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "iid": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["iid", "description"]
            }
        }
      },
      "required": ["uid", "item_sequence"]
    }
    """
    json_deserializer = JSONDeserializer(schema_str,
                                         from_dict=to_dict)

    consumer_conf = {'bootstrap.servers': kwargs["bootstrap_server"],
                     'group.id': kwargs["group"],
                     'auto.offset.reset': "earliest"}

    consumer = Consumer(consumer_conf)
    print(consumer.subscribe([topic]))

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue

            sequence = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
            raw_sequence = [item.iid for item in sequence.item_sequence]
            try:
                p = r_handler.build_recos(raw_sequence, 10)
                print(p)
                with r.pipeline() as pipe:
                    pipe.delete(sequence.uid)
                    pipe.lpush(sequence.uid, *[item.iid for item in p])
                    pipe.execute()
            except ValueError:
                pass

        except KeyboardInterrupt:
            break

    consumer.close()


if __name__ == "__main__":
    main(topic="t1",
         schema_registry="http://localhost:8085",
         bootstrap_server="localhost:29092",
         group="mygroup")
