import uuid
from typing import Optional

import bson
from core import config
from fastapi import Depends
from models.response import Bookmarks, FilmDislikes, FilmLikes, FilmMeanScore, Review, Reviews
from svc.content_getter import Getter, get_getter


class ContentLogic:
    @staticmethod
    async def get_bookmarks(user_id: uuid.UUID, getter: Getter = Depends(get_getter)) -> Optional[Bookmarks]:
        docs = await getter.find_many_document(
            collection=config.BOOKMARKS_COLLECTION, elements={"user_id": bson.Binary.from_uuid(user_id)}
        )
        if docs is None:
            return None
        bookmarks = []
        for doc in docs:
            bookmarks.append(doc["film_id"])
        return Bookmarks(user_id=user_id, reviews_ids=bookmarks)

    @staticmethod
    async def get_reviews(film_id: uuid.UUID, getter: Getter = Depends(get_getter)) -> Optional[Reviews]:
        doc = await getter.find_one_document(
            collection=config.FILM_COLLECTION, elements={"film_id": bson.Binary.from_uuid(film_id)}
        )
        if doc is None:
            return None
        return Reviews(film_id=film_id, reviews=doc["reviews"])

    @staticmethod
    async def get_review(review_id: uuid.UUID, getter: Getter = Depends(get_getter)) -> Optional[Review]:
        doc = await getter.find_one_document(
            collection=config.REVIEW_COLLECTION, elements={"review_id": bson.Binary.from_uuid(review_id)}
        )
        if doc is None:
            return None
        return Review(**doc)

    @staticmethod
    async def get_film_likes(film_id: uuid.UUID, getter: Getter = Depends(get_getter)) -> Optional[FilmLikes]:
        doc = await getter.find_one_document(
            collection=config.REVIEW_COLLECTION, elements={"film_id": bson.Binary.from_uuid(film_id)}
        )
        if doc is None:
            return None
        return FilmLikes(film_id=film_id, likes=doc["likes"])

    @staticmethod
    async def get_film_dislikes(film_id: uuid.UUID, getter: Getter = Depends(get_getter)) -> Optional[FilmDislikes]:
        doc = await getter.find_one_document(
            collection=config.REVIEW_COLLECTION, elements={"film_id": bson.Binary.from_uuid(film_id)}
        )
        if doc is None:
            return None
        return FilmDislikes(film_id=film_id, likes=doc["dislikes"])

    @staticmethod
    async def get_film_mean_score(film_id: uuid.UUID, getter: Getter = Depends(get_getter)) -> Optional[FilmMeanScore]:
        doc = await getter.find_one_document(
            collection=config.REVIEW_COLLECTION, elements={"film_id": bson.Binary.from_uuid(film_id)}
        )
        if doc is None:
            return None
        mean = 0
        for score in doc["scores"]:
            mean += score
        return FilmMeanScore(film_id=film_id, score=mean / len(doc["scores"]))


content_logic: Optional[ContentLogic] = None


def get_content_logic() -> Optional[ContentLogic]:
    return content_logic
