import sys
import uuid
from http import HTTPStatus

from core import config
from fastapi import APIRouter, Depends, HTTPException
from models.body import Bookmark, KafkaBookmark
from models.response import Bookmarks
from svc.content_logic import ContentLogic, get_content_logic
from svc.event_sendler import KafkaEventSendler, get_kafka_event_sendler
from svc.user_parser import JWTUserParser, get_user_parser

if sys.version_info.minor < 8:
    from typing import _Literal as Literal  # type: ignore
else:
    from typing import Literal  # type: ignore


router = APIRouter(prefix="/bookmarks")


@router.post("/film/")
async def bookmarks_film(
    book_mark: Bookmark, kafka_event_sendler: KafkaEventSendler = Depends(get_kafka_event_sendler)
) -> Literal[HTTPStatus.OK]:
    await kafka_event_sendler.post_event(topic=config.BOOKMARKS_TOPIC, event_obj=book_mark, out_obj_class=KafkaBookmark)
    return HTTPStatus.OK


@router.get("/film/{jwt}")
async def user_film_bookmarks(
    jwt: str,
    content_logic: ContentLogic = Depends(get_content_logic),
    user_parser: JWTUserParser = Depends(get_user_parser),
) -> Bookmarks:
    user_id = user_parser.get_user(jwt)
    bm = await content_logic.get_bookmarks(user_id=user_id)
    if bm is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
    return bm
