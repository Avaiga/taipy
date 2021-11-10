from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from taipy.common.alias import CycleId
from taipy.cycle.frequency import Frequency


@dataclass
class CycleModel:
    id: CycleId
    name: str
    frequency: Frequency
    creation_date: str
    start_date: Optional[str]
    end_date: Optional[str]
    properties: dict
