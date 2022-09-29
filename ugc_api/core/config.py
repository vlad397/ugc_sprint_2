import os
from logging import config as logging_config
from typing import List

from core.logger import LOGGING
from pydantic import BaseSettings, Field

logging_config.dictConfig(LOGGING)


class Config(BaseSettings):
    DEBUG: bool = Field(..., default=True, env="DEBUG")
    API_VERSION: str = "v1"
    JWT_SECRET: str = "qwerty"
    PROJECT_NAME: str = Field(..., env="PROJECT_NAME", default="ugc_api")
    KAFKA_HOST: str = Field(..., env="KAFKA_HOST", default="kafka")
    KAFKA_PORT: int = Field(..., env="KAFKA_PORT", default=9092)
    FILM_TIMESTAMP_TOPIC: str = "film_timestamp"
    LIKE_TOPIC: str = "like"
    BOOKMARKS_TOPIC: str = "bookmarks"
    REVIEW_TOPIC: str = "review"

    MONGO_HOST: str = Field(..., env="MONGO_HOST", default="mongo")
    MONGO_PORT: int = Field(..., env="MONGO_PORT", default=27017)
    MONGO_PASSWORD: str = Field(..., env="MONGO_PASSWORD", default="example")
    MONGO_LOGIN: str = Field(..., env="MONGO_LOGIN", default="root")
    MONGO_DB: str = Field(..., env="MONGO_DB", default="test")
    FILM_TIMESTAMP_COLLECTION: str = "film_timestamp"
    LIKE_TOPIC_COLLECTION: str = "like"
    BOOKMARKS_COLLECTION: str = "bookmarks"
    REVIEW_COLLECTION: str = "review"
    FILM_COLLECTION: str = "film"
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TOPICS: List = [FILM_TIMESTAMP_TOPIC, LIKE_TOPIC, BOOKMARKS_TOPIC, REVIEW_TOPIC]
    SENTRY_DSN: str = Field(
        ..., env="SENTRY_DSN", default="https://a291eb96731940709d25c74a85887097@o980582.ingest.sentry.io/6548151"
    )


config = Config()
