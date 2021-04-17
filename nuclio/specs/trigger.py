from typing import Optional, Dict, Union


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
