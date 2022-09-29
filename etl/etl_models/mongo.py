import datetime
import uuid
from typing import List

import bson
from etl_models.base import BasePModel


class Film(BasePModel):
    film_id: bson.Binary
    likes: List[bson.Binary]
    dislikes: List[bson.Binary] = []
    reviews: List[bson.Binary] = []
    scores: List[float]


class Review(BasePModel):
    user_id: bson.Binary
    likes: List[bson.Binary] = []
    dislikes: List[bson.Binary] = []
    review_time: datetime.datetime
    scores: List[float]


class Bookmark(BasePModel):
    user_id: bson.Binary
    film_id: bson.Binary


class FilmTimestamp(BasePModel):
    user_id: bson.Binary
    film_id: bson.Binary
    film_timestamp: datetime.datetime
