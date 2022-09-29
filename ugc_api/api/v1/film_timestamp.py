import sys
from http import HTTPStatus

from core import config
from fastapi import APIRouter, Depends
from models.body import FilmTimeStamp, KafkaFilmTimeStamp
from svc.event_sendler import KafkaEventSendler, get_kafka_event_sendler

if sys.version_info.minor < 8:
    from typing import _Literal as Literal  # type: ignore
else:
    from typing import Literal  # type: ignore


router = APIRouter(prefix="/film_timestamp")


@router.post("/film-timestamp/")
async def film_timestamp(
    film_timestamp: FilmTimeStamp, kafka_event_sendler: KafkaEventSendler = Depends(get_kafka_event_sendler)
) -> Literal[HTTPStatus.OK]:
    await kafka_event_sendler.post_event(
        topic=config.FILM_TIMESTAMP_TOPIC, event_obj=film_timestamp, out_obj_class=KafkaFilmTimeStamp
    )
    return HTTPStatus.OK
