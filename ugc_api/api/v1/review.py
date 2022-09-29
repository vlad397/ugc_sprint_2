import sys
import uuid
from http import HTTPStatus

from core import config
from fastapi import APIRouter, Depends, HTTPException
from models.body import KafkaReview, Review
from models.response import Review as RespReview
from models.response import Reviews
from svc.content_logic import ContentLogic, get_content_logic
from svc.event_sendler import KafkaEventSendler, get_kafka_event_sendler

router = APIRouter(prefix="/review")


if sys.version_info.minor < 8:
    from typing import _Literal as Literal  # type: ignore
else:
    from typing import Literal  # type: ignore


@router.post("/film/")
async def review_film(
    review: Review, kafka_event_sendler: KafkaEventSendler = Depends(get_kafka_event_sendler)
) -> Literal[HTTPStatus.OK]:
    await kafka_event_sendler.post_event(topic=config.REVIEW_TOPIC, event_obj=review, out_obj_class=KafkaReview)
    return HTTPStatus.OK


@router.get("/{review_id}")
async def film_score(review_id: uuid.UUID, content_logic: ContentLogic = Depends(get_content_logic)) -> RespReview:
    ans = await content_logic.get_review(review_id=review_id)
    if ans is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return ans


@router.get("/{film_id}/reviews")
async def film_score_reviews(film_id: uuid.UUID, content_logic: ContentLogic = Depends(get_content_logic)) -> Reviews:
    ans = await content_logic.get_reviews(film_id=film_id)
    if ans is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return ans
