import datetime
import uuid

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BasePModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class BaseFilmEvent(BasePModel):
    film_id: uuid.UUID
    event_time: datetime.datetime


class BaseReviewEvent(BasePModel):
    review_id: uuid.UUID
    event_time: datetime.datetime


class BaseFilmTimeStamp(BaseFilmEvent):
    film_timestamp: datetime.datetime


class BaseLikeFilm(BaseFilmEvent):
    score: int


class BaseLikeReview(BaseReviewEvent):
    score: int
