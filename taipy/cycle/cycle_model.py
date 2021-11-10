from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from taipy.common.alias import CycleId
from taipy.cycle.frequency import Frequency


@dataclass
class CycleModel:
    id: CycleId
    config_name: str
    frequency: Frequency
    creation_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    properties: dict
