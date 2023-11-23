# Copyright 2023 Avaiga Private Limited
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
import re
from datetime import datetime, timedelta


class _Decoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def _str_to_timedelta(self, timedelta_str: str) -> timedelta:
        """
        Parse a time string e.g. (2h13m) into a timedelta object.

        :param timedelta_str: A string identifying a duration.  (eg. 2h13m)
        :return datetime.timedelta: A datetime.timedelta object
        """
        regex = re.compile(
            r"^((?P<days>[\.\d]+?)d)? *"
            r"((?P<hours>[\.\d]+?)h)? *"
            r"((?P<minutes>[\.\d]+?)m)? *"
            r"((?P<seconds>[\.\d]+?)s)?$"
        )
        parts = regex.match(timedelta_str)
        if not parts:
            raise TypeError("Can not deserialize string into timedelta")
        time_params = {name: float(param) for name, param in parts.groupdict().items() if param}
        # mypy has an issue with dynamic keyword parameters, hence the type ignore on the line bellow.
        return timedelta(**time_params)  # type: ignore

    def object_hook(self, source):
        if source.get("__type__") == "Datetime":
            return datetime.fromisoformat(source.get("__value__"))
        if source.get("__type__") == "Timedelta":
            return self._str_to_timedelta(source.get("__value__"))
        else:
            return source


def loads(d):
    return json.loads(d, cls=_Decoder)
