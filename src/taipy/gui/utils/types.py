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
import typing as t
from abc import ABC
from datetime import datetime

from .._warnings import _warn
from . import _date_to_string, _MapDict, _string_to_date, _variable_decode


class _TaipyBase(ABC):
    __HOLDER_PREFIXES: t.Optional[t.List[str]] = None
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
        except:
            return self.__hash_name

    @staticmethod
    def get_hash():
        return NotImplementedError

    @staticmethod
    def _get_holder_prefixes() -> t.List[str]:
        if _TaipyBase.__HOLDER_PREFIXES is None:
            _TaipyBase.__HOLDER_PREFIXES = [cls.get_hash() + "_" for cls in _TaipyBase.__subclasses__()]
        return _TaipyBase.__HOLDER_PREFIXES


class _TaipyData(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "D"


class _TaipyBool(_TaipyBase):
    def get(self):
        return self.cast_value(super().get())

    def cast_value(self, value: t.Any):
        return bool(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "B"


class _TaipyNumber(_TaipyBase):
    def get(self):
        try:
            return float(super().get())
        except Exception as e:
            raise TypeError(f"Variable '{self._get_readable_name()}' should hold a number: {e}")

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
        return _TaipyBase._HOLDER_PREFIX + "N"


class _TaipyLoNumbers(_TaipyBase):
    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            try:
                return list(map(lambda f: float(f), value[1:-1].split(",")))
            except Exception as e:
                _warn(f"{self._get_readable_name()}: Parsing {value} as an array of numbers", e)
                return []
        return super().cast_value(value)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Ln"


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
        return _TaipyBase._HOLDER_PREFIX + "Dt"


class _TaipyLovValue(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Lv"


class _TaipyLov(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "L"


class _TaipyContent(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "C"


class _TaipyContentImage(_TaipyBase):
    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Ci"


class _TaipyDict(_TaipyBase):
    def get(self):
        val = super().get()
        return json.dumps(val._dict if isinstance(val, _MapDict) else val)

    @staticmethod
    def get_hash():
        return _TaipyBase._HOLDER_PREFIX + "Di"
