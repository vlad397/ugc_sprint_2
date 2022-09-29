import asyncio
from asyncio import Task
from typing import Callable, Dict, Iterable, List, Optional, Union

import bson
import orjson
from aiokafka import AIOKafkaConsumer
from etl_core import config
from etl_models.kafka import KafkaBookmark, KafkaFilmTimeStamp, KafkaLikeFilm, KafkaLikeReview, KafkaReview
from etl_models.mongo import Bookmark, Film, FilmTimestamp, Review
from etl_models.state import State
from etl_svc.state import EtlStateRedis
from motor.motor_asyncio import AsyncIOMotorClient


class MongoBackend:
    def __init__(self, mongo: AsyncIOMotorClient, db_name: str):
        self.mongo = mongo[db_name]

    def get_collection(self, collection: str):
        return self.mongo[collection]

    async def insert_document(self, collection_name: str, data):
        collection = self.mongo.get_collection(collection_name)
        return await collection.insert_one(data)

    async def find_one_document(self, collection_name: str, elements):
        collection = self.mongo.get_collection(collection_name)
        return await collection.find_one(elements)

    async def find_many_document(self, collection_name: str, elements) -> Iterable:
        collection = self.mongo.get_collection(collection_name)
        return await collection.find(elements)

    async def update_document(self, collection_name: str, query_elements, new_values):
        collection = self.mongo.get_collection(collection_name)
        await collection.update_one(query_elements, {"$set": new_values})


class KafkaMongoLogic:
    def __init__(self, mongo: MongoBackend):
        self.mongo = mongo

    def get_rule(self, topic) -> Optional[Callable]:
        if topic == config.LIKE_TOPIC:
            return self.like_rule
        elif topic == config.REVIEW_TOPIC:
            return self.review_rule
        elif topic == config.BOOKMARKS_TOPIC:
            return self.bookmarks_rule
        elif topic == config.FILM_TIMESTAMP_TOPIC:
            return self.filmtimestamp_rule
        else:
            return None

    @staticmethod
    def parse_kafka_obj(topic: str, key: bytes, value: bytes):
        loaded_values = orjson.loads(value.decode())
        if key is not None:
            decoded_key = key.decode()
        else:
            decoded_key = None
        if topic == config.LIKE_TOPIC:
            if decoded_key == "film":
                return KafkaLikeFilm(**loaded_values)
            else:
                return KafkaLikeReview(**loaded_values)
        elif topic == config.REVIEW_TOPIC:
            return KafkaReview(**loaded_values)
        elif topic == config.BOOKMARKS_TOPIC:
            return KafkaBookmark(**loaded_values)
        elif topic == config.FILM_TIMESTAMP_TOPIC:
            return KafkaFilmTimeStamp(**loaded_values)
        else:
            return None

    async def like_rule(self, kafka_like_obj: Union[KafkaLikeReview, KafkaLikeFilm]) -> Optional[Union[Review, Film]]:
        if isinstance(kafka_like_obj, KafkaLikeReview):
            object_id_key = "review_id"
            object_class = Review
            collection = config.REVIEW_COLLECTION
        if isinstance(kafka_like_obj, KafkaLikeFilm):
            object_id_key = "film_id"
            object_class = Film
            collection = config.FILM_COLLECTION

        doc = await self.mongo.find_one_document(
            collection_name=collection,
            elements={object_id_key: bson.Binary.from_uuid(getattr(kafka_like_obj, object_id_key))},
        )
        if doc is None:
            # тут быть недолжно для ускорения
            if isinstance(kafka_like_obj, KafkaLikeFilm):
                obj = Film(
                    film_id=bson.Binary.from_uuid(kafka_like_obj.film_id),
                    likes=[],
                    dislikes=[],
                    reviews=[],
                    scores=[],
                )
                await self.mongo.insert_document(collection_name=collection, data=obj.dict())
                return obj
            return None
        doc_id = doc["_id"]
        obj = object_class(**doc)
        if kafka_like_obj.user_id not in obj.likes and kafka_like_obj.score > config.LIKE_LIM:
            obj.likes.append(bson.Binary.from_uuid(kafka_like_obj.user_id))
        if kafka_like_obj.user_id not in obj.dislikes and kafka_like_obj.score <= config.LIKE_LIM:
            obj.dislikes.append(bson.Binary.from_uuid(kafka_like_obj.user_id))
        if kafka_like_obj.user_id in obj.dislikes and kafka_like_obj.score > config.LIKE_LIM:
            obj.likes.append(bson.Binary.from_uuid(kafka_like_obj.user_id))
            obj.dislikes.remove(bson.Binary.from_uuid(kafka_like_obj.user_id))
        if kafka_like_obj.user_id in obj.likes and kafka_like_obj.score <= config.LIKE_LIM:
            obj.dislikes.append(bson.Binary.from_uuid(kafka_like_obj.user_id))
            obj.likes.remove(bson.Binary.from_uuid(kafka_like_obj.user_id))
        await self.mongo.update_document(
            collection_name=collection, new_values=obj.dict(), query_elements={"_id": doc_id}
        )
        return obj

    async def review_rule(self, kafka_review_obj: KafkaReview) -> Optional[Review]:
        rev = Review(
            user_id=bson.Binary.from_uuid(kafka_review_obj.meta.author_id),
            likes=[],
            dislikes=[],
            review_time=kafka_review_obj.meta.review_time,
            scores=[],
        )
        doc = await self.mongo.find_one_document(
            collection_name=config.REVIEW_COLLECTION,
            elements={"review_id": bson.Binary.from_uuid(kafka_review_obj.review_id)},
        )
        if doc is None:
            await self.mongo.insert_document(collection_name=config.REVIEW_COLLECTION, data=rev.dict())
            return rev
        doc_id = doc["_id"]
        await self.mongo.update_document(
            collection_name=config.REVIEW_COLLECTION, new_values=rev.dict(), query_elements={"_id": doc_id}
        )
        return rev

    async def bookmarks_rule(self, kafka_bookmarks_obj: KafkaBookmark) -> Bookmark:
        bm = Bookmark(
            user_id=bson.Binary.from_uuid(kafka_bookmarks_obj.user_id),
            film_id=bson.Binary.from_uuid(kafka_bookmarks_obj.film_id),
        )
        doc = await self.mongo.find_one_document(collection_name=config.BOOKMARKS_COLLECTION, elements=bm.dict())
        if doc is None:
            await self.mongo.insert_document(collection_name=config.BOOKMARKS_COLLECTION, data=bm.dict())
            return bm
        doc_id = doc["_id"]
        await self.mongo.update_document(
            collection_name=config.BOOKMARKS_COLLECTION, new_values=bm.dict(), query_elements={"_id": doc_id}
        )
        return bm

    async def filmtimestamp_rule(self, kafka_filmtimestamp_obj: KafkaFilmTimeStamp) -> FilmTimestamp:
        tf = FilmTimestamp(
            user_id=bson.Binary.from_uuid(kafka_filmtimestamp_obj.user_id),
            film_id=bson.Binary.from_uuid(kafka_filmtimestamp_obj.film_id),
            film_timestamp=kafka_filmtimestamp_obj.film_timestamp,
        )
        doc = await self.mongo.find_one_document(
            collection_name=config.FILM_TIMESTAMP_COLLECTION, elements=tf.dict(exclude={"film_timestamp"})
        )
        if doc is None:
            await self.mongo.insert_document(collection_name=config.FILM_TIMESTAMP_COLLECTION, data=tf.dict())
            return tf
        doc_id = doc["_id"]
        await self.mongo.update_document(
            collection_name=config.FILM_TIMESTAMP_COLLECTION, new_values=tf.dict(), query_elements={"_id": doc_id}
        )
        return FilmTimestamp(**kafka_filmtimestamp_obj.dict())


class EltKafkaMongo:
    def __init__(
        self,
        kafka_consumers: Dict[str, AIOKafkaConsumer],
        mongo: MongoBackend,
        logic: KafkaMongoLogic,
        state: EtlStateRedis,
        loop,
    ):
        self.consumers = kafka_consumers
        self.tasks: List[Task] = []
        self.mongo = mongo
        self.state = state
        self.logic = logic

        self.loop: asyncio.AbstractEventLoop = loop

    async def start(self):
        for cons in self.consumers.values():
            self.tasks.append(asyncio.create_task(self.get_msg(cons)))
        await asyncio.gather(*self.tasks)

    async def get_msg(self, consumer):
        await consumer.start()
        run_consumer = True
        while run_consumer:
            try:
                async for message in consumer:
                    kafka_obj = self.logic.parse_kafka_obj(topic=message.topic, key=message.key, value=message.value)
                    proc_func = self.logic.get_rule(message.topic)
                    await proc_func(kafka_obj)
                    state = State(partition=message.partition, offset=message.offset)
                    await self.state.set_state(message.topic, state)
            except KeyboardInterrupt:
                await consumer.stop()
                run_consumer = False
