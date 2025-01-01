from fastapi import APIRouter, Depends

from typing import List
from .request import UserItemSequence
from .response import UserItemRecommendation, Recommendation

from service import Service
from broker import KafkaWrapper, KafkaWrapperConfig
from kv_storage import RedisStorage

from settings import get_settings, Settings


recommendation = APIRouter()


def settings():
    settings = get_settings()
    return settings


def kv_storage(settings: Settings = Depends(settings)):
    return RedisStorage(host=settings.redis_host,
                        port=settings.redis_port,
                        db=settings.redis_db)


def broker_client(settings: Settings = Depends(settings)):
    config = {"bootstrap_server": f"{settings.broker_host}:{settings.broker_port}",
              "schema_registry_url": f"http://{settings.schemaregisty_host}:{settings.schemaregistry_port}"}
    return KafkaWrapper(config=KafkaWrapperConfig(**config))


def fetch_service(broker_client: KafkaWrapper = Depends(broker_client),
                  key_value_storage: RedisStorage = Depends(kv_storage)):
    return Service(broker_client=broker_client, key_value_storage=key_value_storage)


@recommendation.post("/personal")
def fetch_personal_recommendation(item_sequence: UserItemSequence,
                                  service: Service = Depends(fetch_service)) -> UserItemRecommendation:
    data = service.fetch_recommendations(item_sequence)
    return data


@recommendation.get("/items")
def fetch_items(service: Service = Depends(fetch_service)) -> List[Recommendation]:
    data = service.fetch_items()
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
