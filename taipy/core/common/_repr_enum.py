from enum import Enum


class _ReprEnum(Enum):
    @classmethod
    def _from_repr(cls, repr_: str):
        return next(filter(lambda e: repr(e) == repr_, cls))  # type: ignore
