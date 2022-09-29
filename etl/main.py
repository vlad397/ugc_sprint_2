import asyncio
import socket

import aioredis
from aiokafka import AIOKafkaConsumer
from etl_core import config
from etl_db import kafka, mongo, redis
from etl_svc.etl import EltKafkaMongo, EtlStateRedis, KafkaMongoLogic, MongoBackend
from motor.motor_asyncio import AsyncIOMotorClient


async def startup(loop):
    for topic in config.TOPICS:
        kafka.kafka_consumers[topic] = AIOKafkaConsumer(
            *config.TOPICS,
            bootstrap_servers=[f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"],
            client_id=socket.gethostname(),
            loop=loop,
        )
    redis.redis = aioredis.Redis(
        connection_pool=aioredis.ConnectionPool.from_url(
            f"redis://{config.REDIS_HOST}:{config.REDIS_PORT}", decode_responses=True
        )
    )
    mongo.mongo = AsyncIOMotorClient(f"mongodb://root:example@{config.MONGO_HOST}:{config.MONGO_PORT}/")
    stator = EtlStateRedis(redis=redis.redis)
    mongobackend = MongoBackend(mongo=mongo.mongo, db_name=config.MONGO_DB)
    kml = KafkaMongoLogic(mongo=mongobackend)
    etl_p = EltKafkaMongo(loop=loop, kafka_consumers=kafka.kafka_consumers, mongo=mongobackend, logic=kml, state=stator)
    await etl_p.start()


async def shutdown(loop):
    await redis.redis.close()


if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(startup(loop))
    loop.close()
