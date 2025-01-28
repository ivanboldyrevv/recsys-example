from fastapi import APIRouter, Depends

from typing import List
from .request import UserItemSequence
from .response import UserItemRecommendation, Recommendation

from service import Service
from messaging import KafkaRelay
from key_value import RedisClient

from settings import get_settings, Settings


recommendation = APIRouter()


def settings():
    settings = get_settings()
    return settings


def kv_storage(settings: Settings = Depends(settings)):
    return RedisClient({"host": settings.redis_host,
                        "port": settings.redis_port,
                        "db": settings.redis_db})


def broker_client(settings: Settings = Depends(settings)):
    config = {"bootstrap.servers": f"{settings.broker_host}:{settings.broker_port}",
              "schema.registry.url": f"http://{settings.schemaregisty_host}:{settings.schemaregistry_port}"}
    return KafkaRelay(config)


def fetch_service(broker_client: KafkaRelay = Depends(broker_client),
                  key_value_storage: RedisClient = Depends(kv_storage)):
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
