from etl_models.base import BasePModel

from kafka import TopicPartition


class State(BasePModel):
    partition: int
    offset: int
