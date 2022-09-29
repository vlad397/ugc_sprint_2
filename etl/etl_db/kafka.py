from typing import Dict, Optional

from aiokafka import AIOKafkaConsumer
from kafka.admin import KafkaAdminClient

kafka_consumers: Optional[Dict[str, AIOKafkaConsumer]] = {}
kafka_admin: Optional[KafkaAdminClient] = None


async def get_kafka_producer() -> Optional[Dict[str, AIOKafkaConsumer]]:
    return kafka_consumers


def get_kafka_admin() -> Optional[KafkaAdminClient]:
    return kafka_admin
