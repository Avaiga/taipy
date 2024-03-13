# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class _Encoder(json.JSONEncoder):
    def _timedelta_to_str(self, obj: timedelta) -> str:
        total_seconds = obj.total_seconds()
        return (
            f"{int(total_seconds // 86400)}d"
            f"{int(total_seconds % 86400 // 3600)}h"
            f"{int(total_seconds % 3600 // 60)}m"
            f"{int(total_seconds % 60)}s"
        )

    def default(self, o: Any):
        if isinstance(o, Enum):
            return o.value
        elif isinstance(o, datetime):
            return {"__type__": "Datetime", "__value__": o.isoformat()}
        elif isinstance(o, timedelta):
            return {"__type__": "Timedelta", "__value__": self._timedelta_to_str(o)}
        else:
            return json.JSONEncoder.default(self, o)


def dumps(d):
    return json.dumps(d, cls=_Encoder)
