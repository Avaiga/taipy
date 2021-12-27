from dataclasses import dataclass

from dataclasses_json.api import dataclass_json

from taipy.common.alias import CycleId
from taipy.common.frequency import Frequency


@dataclass_json
@dataclass
class CycleModel:
    id: CycleId
    name: str
    frequency: Frequency
    properties: dict
    creation_date: str
    start_date: str
    end_date: str
