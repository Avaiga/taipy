from abc import ABC
from datetime import datetime
import typing as t
import warnings

from . import date_to_ISO, ISO_to_date


class TaipyBase(ABC):
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


class TaipyData(TaipyBase):
    pass


class TaipyBool(TaipyBase):
    def get(self):
        return self.cast_value(super().get())

    def cast_value(self, value: t.Any):
        return bool(value)


class TaipyNumber(TaipyBase):
    def get(self):
        try:
            return float(super().get())
        except ValueError:
            raise ValueError(f"Variable {self.get_name()} should hold a number")

    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            try:
                return float(value) if value else 0.0
            except Exception as e:
                warnings.warn(f"{self.get_name()}: Parsing {value} as float:\n{e}")
                return 0.0
        else:
            super().cast_value(value)


class TaipyDate(TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, datetime):
            val = date_to_ISO(val)
        elif val is not None:
            val = str(val)
        return val

    def cast_value(self, value: t.Any):
        if isinstance(value, str):
            return ISO_to_date(value)
        return super().cast_value(value)


class TaipyLovValue(TaipyBase):
    pass


class TaipyLov(TaipyBase):
    pass


class TaipyContent(TaipyBase):
    pass


class TaipyContentImage(TaipyBase):
    pass
