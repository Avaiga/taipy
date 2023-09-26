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

import typing as t
from datetime import date, datetime, time

from dateutil import parser
from pytz import utc

from .._warnings import _warn


def _date_to_ISO(date_val: t.Union[datetime, date, time]) -> str:
    if isinstance(date_val, datetime):
        # return date.isoformat() + 'Z', if possible
        try:
            return date_val.astimezone(utc).isoformat()
        except Exception as e:
            # astimezone() fails on Windows for pre-epoch times
            # See https://bugs.python.org/issue36759
            _warn("Exception raised converting date to ISO 8601", e)
    return date_val.isoformat()


def _ISO_to_date(date_str: str) -> datetime:
    # return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
    # return datetime.fromisoformat(date_str)
    return parser.parse(date_str)
