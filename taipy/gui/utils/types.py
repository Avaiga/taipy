# Copyright 2021-2025 Avaiga Private Limited
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
import typing as t
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping
from datetime import datetime
from enum import Enum
from inspect import ismethod

from .._warnings import _warn
from ..json_properties import JsonableProperty, JsonProperty
from . import _date_to_string, _MapDict, _string_to_date, _variable_decode


class _DoNotUpdate:
    def __repr__(self):
        return "Taipy: Do not update"


class HolderSuffixes(Enum):
    DATA = "D"
    BOOL = "B"
    NUMBER = "N"
    LO_NUMBERS = "Ln"
    DATE = "Dt"
    DATE_RANGE = "Dr"
    LOV_VALUE = "Lv"
    LOV = "L"
    CONTENT = "C"
    CONTENT_IMAGE = "Ci"
    CONTENT_HTML = "Ch"
    DICT = "Di"
    TIME = "Tm"
    JSONABLE = "J"
    JSON = "Tj"


class _TaipyBase(ABC):
    __HOLDER_PREFIXES: t.Optional[list[str]] = None
    _HOLDER_PREFIX = "_Tp"

    def __init__(self, data: t.Any, hash_name: str) -> None:
        self.__data = data
        self.__hash_name = hash_name

    def get(self):
        return self.__data

    def get_name(self):
        return self.__hash_name

    def set(self, data: t.Any):
        self.__data = data

    def cast_value(self, value: t.Any):
        return value

    def _get_readable_name(self):
        try:
            name, mod = _variable_decode(
                self.__hash_name[5:] if self.__hash_name.startswith("tpec_") else self.__hash_name
            )
            return name if mod is None or mod == "__main__" else f"{mod}.{name}"
        except BaseException:
            return self.__hash_name

    @staticmethod
    @abstractmethod
    def get_hash():
        raise NotImplementedError

    @staticmethod
    def _get_holder_prefixes() -> list[str]:
        if _TaipyBase.__HOLDER_PREFIXES is None:
            _TaipyBase.__HOLDER_PREFIXES = [cls.get_hash() + "_" for cls in _TaipyBase.__subclasses__()]
        return _TaipyBase.__HOLDER_PREFIXES


class _TaipyData(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.DATA.value


class _TaipyBool(_TaipyBase):
    def get(self):
        return self.cast_value(super().get())

    def cast_value(self, value: t.Any):
        return bool(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.BOOL.value


class _TaipyNumber(_TaipyBase):
    def get(self):
        if super().get() is None:
            return None
        try:
            return float(super().get())
        except Exception as e:
            raise TypeError(f"Variable '{self._get_readable_name()}' should hold a number: {e}") from None

    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            try:
                return float(value) if value else 0.0
            except Exception as e:
                _warn(f"{self._get_readable_name()}: Parsing {value} as float", e)
                return 0.0
        return super().cast_value(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.NUMBER.value


class _TaipyLoNumbers(_TaipyBase):
    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            try:
                return [float(f) for f in value[1:-1].split(",")]
            except Exception as e:
                _warn(f"{self._get_readable_name()}: Parsing {value} as an array of numbers", e)
                return []
        return super().cast_value(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.LO_NUMBERS.value


class _TaipyDate(_TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, datetime):
            val = _date_to_string(val)
        elif val is not None:
            val = str(val)
        return val

    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            return _string_to_date(value)
        return super().cast_value(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.DATE.value


class _TaipyDateRange(_TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, list):
            return [_date_to_string(v) if isinstance(v, datetime) else None if v is None else str(v) for v in val]
        return val

    def cast_value(self, value: t.Any):
        if isinstance(value, list):
            return [_string_to_date(v) if isinstance(v, str) else str(v) for v in value]
        return super().cast_value(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.DATE_RANGE.value


class _TaipyLovValue(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.LOV_VALUE.value


class _TaipyLov(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.LOV.value


class _TaipyContent(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.CONTENT.value


class _TaipyContentImage(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.CONTENT_IMAGE.value


class _TaipyContentHtml(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.CONTENT_HTML.value


class _TaipyDict(_TaipyBase):
    def get(self):
        val = super().get()
        return json.dumps(val._dict if isinstance(val, _MapDict) else val)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.DICT.value


class _TaipyTime(_TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, datetime):
            val = _date_to_string(val)
        elif val is not None:
            val = str(val)
        return val

    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return super().cast_value(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.TIME.value


class _TaipyToJsonable(_TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, JsonableProperty):
            try:
                return val.to_jsonable()
            except Exception as e:
                _warn(f"Issue while deserializing object of type {type(val).__name__} (JsonableProperty).", e)
        elif isinstance(val, JsonProperty):
            try:
                return json.loads(val.to_json())
            except Exception as e:
                _warn(f"Issue while deserializing object of type {type(val).__name__} (JsonProperty).", e)
        elif isinstance(val, (Mapping, Iterable)):
            return val._dict if isinstance(val, _MapDict) else list(val) if isinstance(val, set) else val
        elif (method := getattr(val, "to_jsonable", None)) or (method := getattr(val, "to_dict", None)):
            if ismethod(method):
                try:
                    return method()
                except Exception as e:
                    _warn(
                        f"Issue while serializing object of type {type(val).__name__} "
                        + f"using '{self._get_readable_name()}.{method.__name__}()'.",
                        e,
                    )
            else:
                _warn(f"'{self._get_readable_name()}.{method.__name__}' is not a valid method.")
        elif val is not None:
            _warn(f"'{self._get_readable_name()}.to_jsonable()' must be defined.")
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.JSONABLE.value


class _TaipyToJson(_TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, JsonProperty):
            try:
                return val.to_json()
            except Exception as e:
                _warn(f"Issue while invoking to_json() on object of type {type(val).__name__} (JsonProperty).", e)
        elif (method := getattr(val, "to_json", None)) and ismethod(method):
            try:
                return method()
            except Exception as e:
                _warn(
                    f"Issue while invoking to_json() on object of type {type(val).__name__} "
                    + f"using '{self._get_readable_name()}.to_json()'.",
                    e,
                )
        elif val is not None:
            _warn(f"'{self._get_readable_name()}.to_json()' must be defined.")
        return None

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + HolderSuffixes.JSON.value


__all__ = ["_TaipyToJson", "_TaipyToJsonable"]
