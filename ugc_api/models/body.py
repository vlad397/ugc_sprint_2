import datetime
import uuid
from typing import List

from models.base import BaseFilmEvent, BaseFilmTimeStamp, BaseLikeFilm, BaseLikeReview, BasePModel


class FilmTimeStamp(BaseFilmTimeStamp):
    jwt: str


class KafkaFilmTimeStamp(BaseFilmTimeStamp):
    user_id: uuid.UUID


class LikeFilm(BaseLikeFilm):
    jwt: str


class KafkaLikeFilm(BaseLikeFilm):
    user_id: uuid.UUID


class LikeFilmReview(BaseLikeReview):
    jwt: str


class KafkaLikeReview(BaseLikeReview):
    user_id: uuid.UUID


class MetaReview(BasePModel):
    author_id: uuid.UUID
    review_time: datetime.datetime


class BaseReview(BaseFilmEvent):
    meta: MetaReview
    review_id: uuid.UUID


class Review(BaseReview):
    jwt: str


class KafkaReview(BaseReview):
    user_id: uuid.UUID


class Bookmark(BaseFilmEvent):
    jwt: str


class KafkaBookmark(BaseFilmEvent):
    user_id: uuid.UUID
