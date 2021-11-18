from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json.api import dataclass_json

from taipy.common.alias import CycleId
from taipy.cycle.frequency import Frequency


@dataclass_json
@dataclass
class CycleModel:
    id: CycleId
    name: str
    frequency: Frequency
    properties: dict
    creation_date: str
    start_date: Optional[str]
    end_date: Optional[str]
