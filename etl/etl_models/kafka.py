import datetime
import uuid

from etl_models.base import BaseFilmEvent, BaseFilmTimeStamp, BaseLikeFilm, BaseLikeReview, BasePModel


class KafkaFilmTimeStamp(BaseFilmTimeStamp):
    user_id: uuid.UUID


class KafkaLikeFilm(BaseLikeFilm):
    user_id: uuid.UUID


class KafkaLikeReview(BaseLikeReview):
    user_id: uuid.UUID


class MetaReview(BasePModel):
    author_id: uuid.UUID
    review_time: datetime.datetime


class BaseReview(BaseFilmEvent):
    meta: MetaReview
    review_id: uuid.UUID


class KafkaReview(BaseReview):
    user_id: uuid.UUID
    review_id: uuid.UUID


class KafkaBookmark(BaseFilmEvent):
    user_id: uuid.UUID
