import logging

from settings import get_settings
from builder import RecommendationBuilder
from nosql import RedisStorage
from recbole.quick_start import load_data_and_model
from dto import Item, UserItemSequence

from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer


def to_dict(obj, ctx):
    if obj is None:
        return None

    sequence = UserItemSequence(
        uid=obj["uid"],
        item_sequence=[Item(item["iid"], item["description"]) for item in obj["item_sequence"]]
    )

    return sequence


def read_schema(path):
    with open(path, "r") as data:
        json_schema = data.read()
    return json_schema


def main(topic, recommendation_builder, nosql):
    logger = logging.getLogger("model logger")
    logging.basicConfig(level=logging.INFO)

    schema_str = read_schema("./json_schemas/item_sequence.json")
    json_deserializer = JSONDeserializer(schema_str,
                                         from_dict=to_dict)

    consumer = Consumer({"bootstrap.servers": "kafka1:9092",
                         "group.id": "mygroup",
                         "auto.offset.reset": "earliest"})
    consumer.subscribe([topic])

    while True:
        try:
            msg = consumer.poll(0.5)
            if msg is None:
                continue

            try:
                sequence = json_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
            except Exception:
                continue

            raw_sequence = [item.iid for item in sequence.item_sequence]

            try:
                p = recommendation_builder.build_recos(raw_sequence, 30)
                nosql.set(sequence.uid, [item.iid for item in p])
                logger.info(f"predictions FOR UID: {sequence.uid} successfully delivered!")
            except Exception as e:
                logger.warning(f"an error occurred: {e}")

        except KeyboardInterrupt:
            break

    consumer.close()


if __name__ == "__main__":
    settings = get_settings()

    _, model, dataset, *_ = load_data_and_model(model_file=f"./saved/{settings.model_name}.pth")
    rbuilder = RecommendationBuilder(dataset=dataset,
                                     model=model)

    redis = RedisStorage({"host": settings.redis_host,
                          "port": settings.redis_port,
                          "db": settings.redis_db})

    main("item-sequences", rbuilder, redis)
