from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from taipy.common.alias import CycleId, ScenarioId
from taipy.cycle.dimension import Dimension


@dataclass
class CycleModel:
    id: CycleId
    config_name: str
    dimension: Dimension
    scenarios: List[ScenarioId]
    creation_date: datetime
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    properties: dict
