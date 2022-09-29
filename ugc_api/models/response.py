import datetime
import uuid
from typing import List

from models.base import BasePModel


class FilmLikes(BasePModel):
    film_id: uuid.UUID
    likes: List[uuid.UUID]


class FilmDislikes(BasePModel):
    film_id: uuid.UUID
    dislikes: List[uuid.UUID]


class ReviewLikes(BasePModel):
    review_id: uuid.UUID
    likes: List[uuid.UUID]


class ReviewDislikes(BasePModel):
    film_id: uuid.UUID
    dislikes: List[uuid.UUID]


class FilmMeanScore(BasePModel):
    film_id: uuid.UUID
    score: float


class Bookmarks(BasePModel):
    user_id: uuid.UUID
    bookmarks: List[uuid.UUID]


class Reviews(BasePModel):
    film_id: uuid.UUID
    review: List[uuid.UUID]


class Review(BasePModel):
    user_id: uuid.UUID
    likes: List[uuid.UUID]
    dislikes: List[uuid.UUID]
    review_time: datetime.datetime
    scores: List[float]
