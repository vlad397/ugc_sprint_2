import sys
import uuid
from http import HTTPStatus

from core import config
from fastapi import APIRouter, Depends, HTTPException
from models.body import KafkaLikeFilm, KafkaLikeReview, LikeFilm, LikeFilmReview
from models.response import FilmDislikes, FilmLikes, FilmMeanScore, ReviewDislikes, ReviewLikes
from svc.content_logic import ContentLogic, get_content_logic
from svc.event_sendler import KafkaEventSendler, get_kafka_event_sendler

if sys.version_info.minor < 8:
    from typing import _Literal as Literal  # type: ignore
else:
    from typing import Literal  # type: ignore


router = APIRouter(prefix="/like")


@router.post("/film/")
async def like_film(
    like_film: LikeFilm, kafka_event_sendler: KafkaEventSendler = Depends(get_kafka_event_sendler)
) -> Literal[HTTPStatus.OK]:
    await kafka_event_sendler.post_event(
        topic=config.LIKE_TOPIC, event_obj=like_film, out_obj_class=KafkaLikeFilm, key="film"
    )
    return HTTPStatus.OK


@router.post("/review/")
async def like_review(
    like_film_review: LikeFilmReview, kafka_event_sendler: KafkaEventSendler = Depends(get_kafka_event_sendler)
) -> Literal[HTTPStatus.OK]:
    await kafka_event_sendler.post_event(
        topic=config.LIKE_TOPIC, event_obj=like_film_review, out_obj_class=KafkaLikeReview, key="review"
    )
    return HTTPStatus.OK


@router.get("/film/like/{film_id}")
async def film_likes(film_id: uuid.UUID, content_logic: ContentLogic = Depends(get_content_logic)) -> FilmLikes:
    ans = await content_logic.get_film_likes(film_id=film_id)
    if ans is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return ans


@router.get("/film/dislike/{film_id}")
async def film_dislikes(film_id: uuid.UUID, content_logic: ContentLogic = Depends(get_content_logic)) -> FilmDislikes:
    ans = await content_logic.get_film_dislikes(film_id=film_id)
    if ans is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return ans


@router.get("/film/score/{film_id}")
async def film_score(film_id: uuid.UUID, content_logic: ContentLogic = Depends(get_content_logic)) -> FilmMeanScore:
    ans = await content_logic.get_film_mean_score(film_id=film_id)
    if ans is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return ans
