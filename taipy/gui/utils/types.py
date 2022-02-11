from abc import ABC
from datetime import datetime
import typing as t

from . import dateToISO


class TaipyBase(ABC):
    def __init__(self, data: t.Any, hash_name: str) -> None:
        self.__data = data
        self.__hash_name = hash_name

    def get(self):
        return self.__data

    def get_name(self):
        return self.__hash_name


class TaipyData(TaipyBase):
    pass


class TaipyBool(TaipyBase):
    def get(self):
        return bool(super().get())


class TaipyNumber(TaipyBase):
    def get(self):
        try:
            return float(super().get())
        except ValueError:
            raise ValueError(f"Variable {self.get_name()} should hold a number")


class TaipyDate(TaipyBase):
    def get(self):
        val = super().get()
        if isinstance(val, datetime):
            val = dateToISO(val)
        elif val is not None:
            val = str(val)
        return val


class TaipyLovValue(TaipyBase):
    pass


class TaipyLov(TaipyBase):
    pass


class TaipyContent(TaipyBase):
    pass


class TaipyContentImage(TaipyBase):
    pass
