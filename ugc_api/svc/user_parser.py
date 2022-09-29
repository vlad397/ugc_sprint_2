import abc
import uuid
from abc import ABC
from typing import Optional

import jwt
from core import config


class UserParser(ABC):
    @abc.abstractmethod
    def get_user(self, *args, **kwargs) -> uuid.UUID:
        pass


class JWTUserParser(UserParser):
    def get_user(self, jwt_token: str) -> uuid.UUID:  # type: ignore
        data = jwt.decode(jwt_token, config.JWT_SECRET, algorithms=["HS256"])
        return data["user_id"]


user_parser: Optional[JWTUserParser] = None


def get_user_parser() -> Optional[JWTUserParser]:
    return user_parser
