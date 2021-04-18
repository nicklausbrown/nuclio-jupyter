
import enum
from typing import Optional, Dict, Union, List
from pydantic import Field

from nuclio.specs import CamelBaseModel


class CronTrigger(CamelBaseModel):

    kind: str = 'cron'

    class Attributes(CamelBaseModel):
        schedule: str = None
        interval: str = None
        concurrency: Optional[str] = None
        job_back_off_limit: Optional[int] = None

        class Event(CamelBaseModel):
            body: str = None
            headers: Dict[str, Union[str, int]] = None

        event: Event = Event()

    attributes: Attributes = Attributes()

    def __init__(self, **data):
        super().__init__(**data)

        if 'schedule' in data.keys():
            self.attributes.schedule = data['schedule']
        elif 'interval' in data.keys():
            self.attributes.interval = data['interval']


class KafkaOffsetOptions(enum.Enum):
    earliest = 'earliest'
    latest = 'latest'


class KafkaWorkerAllocationModeOptions(enum.Enum):
    static = 'static'
    pool = 'pool'


class KafkaTrigger(CamelBaseModel):

    kind: str = 'kafka-cluster'

    class Attributes(CamelBaseModel):

        consumer_group: str = None
        topics: List[str] = Field(default_factory=lambda x: list())
        brokers: List[str] = Field(default_factory=lambda x: list())
        partitions: List[int] = Field(default_factory=lambda x: list())

        initial_offset: Optional[KafkaOffsetOptions] = None
        session_timeout: Optional[str] = None
        heartbeat_interval: Optional[str] = None
        worker_allocation_mode: Optional[KafkaWorkerAllocationModeOptions] = None

        fetch_min: Optional[int] = None
        fetch_default: Optional[int] = None
        fetch_max: Optional[int] = None
        channel_buffer_size: Optional[int] = None
        max_processing_time: Optional[str] = None

        rebalance_timeout: Optional[str] = None
        rebalance_max_try: Optional[int] = None
        rebalance_retry_timeout: Optional[str] = None
        max_wait_handler_during_rebalance: Optional[str] = None

