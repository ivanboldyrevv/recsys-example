from fastapi import APIRouter, Depends

from .request import UserItemSequence
from .response import UserItemRecommendation

from service import Service
from broker import KafkaWrapper, KafkaWrapperConfig
from key_value_storage import RedisStorage


recommendation = APIRouter()


def key_value_storage():
    return RedisStorage()


def broker_client():
    return KafkaWrapper(config=KafkaWrapperConfig(bootstrap_server="localhost:29092",
                                                  schema_registry_url="http://localhost:8085"))


def fetch_service(broker_client: KafkaWrapper = Depends(broker_client),
                  key_value_storage: RedisStorage = Depends(key_value_storage)):
    return Service(broker_client=broker_client, key_value_storage=key_value_storage)


@recommendation.post("/personal")
def fetch_personal_recommendation(item_sequence: UserItemSequence,
                                  service: Service = Depends(fetch_service)) -> UserItemRecommendation:
    print(item_sequence)
    data = service.fetch_recommendations(item_sequence)
    return data


# for test
"""
{
  "uid": "t-1-e-3-s-4-t",
  "item_sequence": [
    {
      "iid": "22138",
      "description": "BAKING SET 9 PIECE RETROSPOT"
    },
    {
      "iid": "23254",
      "description": "CHILDRENS CUTLERY DOLLY GIRL"
    }
  ]
}
"""
