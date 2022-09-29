import abc
import uuid
from abc import ABC
from typing import Iterable, Optional

import backoff
import requests
from motor.motor_asyncio import AsyncIOMotorClient


class Getter(ABC):
    @abc.abstractmethod
    async def find_many_document(self, collection: str, elements) -> Iterable:
        pass

    @abc.abstractmethod
    async def find_one_document(self, collection: str, elements):
        pass


class MongoGetter(Getter):
    def __init__(self, client: AsyncIOMotorClient, db_name: str):
        self.client = client[db_name]

    @backoff.on_exception(backoff.expo, requests.exceptions.Timeout)
    def get_collection(self, collection: str):
        return self.client[collection]

    @backoff.on_exception(backoff.expo, requests.exceptions.Timeout)
    async def find_one_document(self, collection_name: str, elements):
        collection = self.client.get_collection(collection_name)
        return await collection.find_one(elements)

    @backoff.on_exception(backoff.expo, requests.exceptions.Timeout)
    async def find_many_document(self, collection_name: str, elements) -> Iterable:
        collection = self.client.get_collection(collection_name)
        return await collection.find(elements)


db_getter: Optional[MongoGetter] = None


def get_getter() -> Optional[MongoGetter]:
    return db_getter
