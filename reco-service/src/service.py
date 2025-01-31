from messaging import BrokerClient
from key_value import Storage

from transport.request import UserItemSequence
from transport.response import UserItemRecommendation, Recommendation

from models import ItemModel


class Service:
    def __init__(self, broker_client: BrokerClient, key_value_storage: Storage):
        self.broker_client: BrokerClient = broker_client
        self.key_value_storage: Storage = key_value_storage

    def fetch_items(self):
        """
            This method, logically, should be located in another service,
            for example, in the service for issuing things, but since this
            is an educational project, it is located here
        """
        items = [Recommendation(iid=i.item_id,
                                description=i.description,
                                image_url=i.image_url) for i in ItemModel.select()]
        return items

    def fetch_recommendations(self, item_sequence: UserItemSequence) -> UserItemRecommendation:
        """
            Method for waking up a model via a broker.
            Then further extraction of the model calculation from the key-value
            storage and generation of the answer.

            args:
                item_sequence: The sequence of objects with which the user interacted
        """
        self.broker_client.produce(topic="item-sequences",
                                   value=item_sequence.model_dump(),
                                   subject_name="itemSequence")

        self.key_value_storage.delete(item_sequence.uid)

        raw_item_ids = list()
        while not raw_item_ids:
            raw_item_ids = self.key_value_storage.get(item_sequence.uid)
        r = UserItemRecommendation(uid=item_sequence.uid)

        for raw_iid in raw_item_ids:
            from_sql = ItemModel.select().where(ItemModel.item_id == raw_iid).get()
            r.recommendations.append(
                Recommendation(iid=from_sql.item_id,
                               description=from_sql.description,
                               image_url=from_sql.image_url)
            )

        return r

    def read_schema_from_file(self, path: str) -> str:
        with open(path) as data:
            json_schema = data.read()
        return json_schema
