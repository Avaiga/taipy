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
from __future__ import annotations

import typing as t
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from json import JSONEncoder
from pathlib import Path
from types import FunctionType, LambdaType

from flask.json.provider import DefaultJSONProvider

from .._warnings import _warn
from ..icon import Icon
from ..utils import _date_to_string, _MapDict, _TaipyBase
from ..utils.singleton import _Singleton


class JsonResolver(ABC):
    def register(self):
        _TaipyJsonResolver().register(self)

    @abstractmethod
    def resolve(self, o) -> t.Union[t.Any, None]:
        return None


class _DefaultJsonResolver(JsonResolver):
    def resolve(self, o):
        if isinstance(o, Icon):
            return o._to_dict()
        if isinstance(o, _MapDict):
            return o._dict
        if isinstance(o, _TaipyBase):
            return o.get()
        if isinstance(o, (datetime, date, time)):
            return _date_to_string(o)
        if isinstance(o, Path):
            return str(o)
        if isinstance(o, FunctionType):
            return o.__name__
        if isinstance(o, LambdaType):
            return str(o)


class _TaipyJsonResolver(object, metaclass=_Singleton):
    def __init__(self):
        self._resolver: t.List[JsonResolver] = []
        self.register(_DefaultJsonResolver())

    def register(self, resolver: JsonResolver):
        self._resolver.append(resolver)

    def resolve(self, o):
        try:
            for resolver in self._resolver:
                if (output := resolver.resolve(o)) is not None:
                    return output
            raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")
        except Exception as e:
            _warn("Exception while resolving JSON", e)
            return None


class _TaipyJsonEncoder(JSONEncoder):
    def default(self, o):
        return _TaipyJsonResolver().resolve(o)


class _TaipyJsonProvider(DefaultJSONProvider):
    default = staticmethod(_TaipyJsonResolver().resolve)  # type: ignore
    sort_keys = False
