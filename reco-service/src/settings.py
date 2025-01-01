import logging
import os

from dataclasses import dataclass
from functools import lru_cache


logger = logging.getLogger("settings")


@dataclass
class Settings:
    db_host: str = os.getenv("POSTGRES_HOST")
    db_port: int = os.getenv("POSTGRES_PORT")
    db_user: str = os.getenv("POSTGRES_USER")
    db_password: str = os.getenv("POSTGRES_PASSWORD")
    db_name: str = os.getenv("POSTGRES_DB")

    broker_host: str = os.getenv("BROKER_HOST")
    broker_port: int = os.getenv("BROKER_PORT")
    topic: str = os.getenv("BROKER_TOPIC")

    schemaregisty_host: str = os.getenv("SCHEMAREGISTRY_HOST")
    schemaregistry_port: int = os.getenv("SCHEMAREGISTRY_PORT")

    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = os.getenv("REDIS_PORT")
    redis_db: int = os.getenv("REDIS_DB")


@lru_cache
def get_settings() -> Settings:
    logger.info("Loading settings from the environment...")
    return Settings()
