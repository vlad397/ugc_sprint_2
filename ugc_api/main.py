import socket

import sentry_sdk
from aiokafka import AIOKafkaProducer
from api import v1
from core import config
from db import kafka, mongo
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from svc import content_getter, content_logic, event_producer, event_sendler
from svc.content_getter import MongoGetter
from svc.content_logic import ContentLogic

from kafka import KafkaAdminClient

app = FastAPI(
    title=config.PROJECT_NAME,
    docs_url="/api/docs",
    openapi_url="/api/docs.json",
    default_response_class=ORJSONResponse,
    debug=config.DEBUG,
)

if config.SENTRY_DSN:
    sentry_sdk.init(dsn=config.SENTRY_DSN)
    app = SentryAsgiMiddleware(app)


@app.on_event("startup")
async def startup():
    kafka.kafka_admin = KafkaAdminClient(
        bootstrap_servers=f"{config.KAFKA_HOST}:{config.KAFKA_PORT}", client_id=socket.gethostname()
    )
    kafka.kafka_producer = AIOKafkaProducer(
        bootstrap_servers=[f"{config.KAFKA_HOST}:{config.KAFKA_PORT}"], client_id=socket.gethostname()
    )
    await kafka.kafka_producer.start()
    mongo.mongo = AsyncIOMotorClient(
        f"mongodb://{config.MONGO_LOGIN}:{config.MONGO_PASSWORD}@{config.MONGO_HOST}:{config.MONGO_PORT}/"
    )
    content_getter.db_getter = MongoGetter(client=mongo.mongo, db_name=config.MONGO_DB)
    content_logic.content_logic = ContentLogic()
    event_producer.kafka_event_producer = event_producer.KafkaEventProducer(
        event_producer=kafka.kafka_producer,
        kafka_admin=kafka.kafka_admin,
        topics=set(config.TOPICS),
    )
    event_sendler.kafka_event_sendler = event_sendler.KafkaEventSendler(
        event_producer=event_producer.kafka_event_producer
    )


@app.on_event("shutdown")
async def shutdown():
    await kafka.kafka_producer.stop()
    kafka.kafka_admin.close()


app.include_router(v1.router, prefix="/api", tags=["ugc"])
