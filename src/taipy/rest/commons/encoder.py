import json
from typing import Any, Union
from datetime import datetime
from enum import Enum



Json = Union[dict, list, str, int, float, bool, None]

class _CustomEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Json:
        if isinstance(o, Enum):
            result = o.value
        elif isinstance(o, datetime):
            result = {"__type__": "Datetime", "__value__": o.isoformat()}
        else:
            result = json.JSONEncoder.default(self, o)
        return result
