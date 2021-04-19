from enum import Enum
from typing import Optional, Dict, Union, List
from pydantic import Field, SecretStr

from nuclio.specs import CamelBaseModel


class CronTrigger(CamelBaseModel):

    kind: str = 'cron'
    max_workers: Optional[int] = 1

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


class KafkaOffsetOptions(Enum):
    earliest = 'earliest'
    latest = 'latest'


class KafkaWorkerAllocationModeOptions(Enum):
    static = 'static'
    pool = 'pool'


class KafkaTrigger(CamelBaseModel):

    kind: str = 'kafka-cluster'
    max_workers: Optional[int] = 1

    class Attributes(CamelBaseModel):

        consumer_group: str = None
        topics: List[str] = Field(default_factory=lambda: list())
        brokers: List[str] = Field(default_factory=lambda: list())
        partitions: List[int] = Field(default_factory=lambda: list())

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

    attributes: Attributes = Attributes()


class V3ioOffsetOptions(Enum):
    earliest = 'Earliest'
    latest = 'Latest'


class V3ioStreamTrigger(CamelBaseModel):

    kind: str = 'v3ioStream'
    max_workers: int = 1

    url: str = 'http://v3io-webapi:8081/'
    password: SecretStr = None

    class Attributes(CamelBaseModel):

        consumer_group: str = None
        container_name: str = None
        stream_path: str = None

        seek_to: Optional[V3ioOffsetOptions] = None
        heartbeat_interval: Optional[str] = None
        polling_interval_ms: Optional[int] = None
        read_batch_size: Optional[int] = None
        sequence_number_commit_interval: Optional[str] = None
        session_timeout: Optional[str] = None

    attributes: Attributes = Attributes()


class HttpIngresses(CamelBaseModel):
    host: str = None
    paths: List[str] = Field(default_factory=lambda: list())


class HttpCORS(CamelBaseModel):
    enabled: bool = True
    allow_origins: Optional[List[str]] = None
    allow_methods: Optional[List[str]] = None
    allow_headers: Optional[List[str]] = None
    allow_credentials: Optional[bool] = None
    preflight_max_age_seconds: Optional[int] = None


class HttpServiceOptions(Enum):
    internal = 'ClusterIP'
    external = 'NodePort'


class HttpTrigger(CamelBaseModel):

    kind: str = 'http'
    max_workers: Optional[int] = 1

    class Attributes(CamelBaseModel):

        port: Optional[int] = None
        max_request_body_size: Optional[int] = None
        read_buffer_size: Optional[int] = None

        ingresses: Optional[Dict[str, HttpIngresses]] = Field(default_factory=lambda: dict())
        cors: Optional[HttpCORS] = None

        service_type: Optional[HttpServiceOptions] = None

    attributes: Attributes = Attributes()
