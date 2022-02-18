from enum import Enum


class ReprEnum(Enum):
    @classmethod
    def from_repr(cls, repr_: str):
        return next(filter(lambda e: repr(e) == repr_, cls))  # type: ignore
