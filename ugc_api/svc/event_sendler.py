import abc
import uuid
from abc import ABC
from typing import Optional

from fastapi import Depends
from models.body import FilmTimeStamp, KafkaFilmTimeStamp
from svc.event_producer import EventProducer, KafkaEventProducer
from svc.user_parser import JWTUserParser, UserParser, get_user_parser


class EventSendler(ABC):
    event_producer: EventProducer

    @abc.abstractmethod
    def get_user(self, *args, **kwargs) -> uuid.UUID:
        pass

    @abc.abstractmethod
    def post_event(self, event_obj, out_obj_class, topic):
        pass


class KafkaEventSendler(EventSendler):
    event_producer: KafkaEventProducer

    def __init__(self, event_producer):
        self.event_producer = event_producer

    def post_event(self, event_obj, out_obj_class, topic: str, key: Optional[str] = None):
        user_id = self.get_user(event_obj.jwt)
        if key is not None:
            encoded_key = key.encode()
        else:
            encoded_key = None
        return self.event_producer.send(
            key=encoded_key, topic=topic, value=out_obj_class(user_id=user_id, **event_obj.dict()).json().encode()
        )

    def get_user(self, jwt_token: str, user_parser: JWTUserParser = Depends(get_user_parser)) -> uuid.UUID:  # type: ignore
        return user_parser.get_user(jwt_token)


kafka_event_sendler: Optional[KafkaEventSendler] = None


def get_kafka_event_sendler() -> Optional[KafkaEventSendler]:
    return kafka_event_sendler
