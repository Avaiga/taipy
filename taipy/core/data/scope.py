from taipy.core.common._repr_enum import _ReprEnum


class _OrderedEnum(_ReprEnum):
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class Scope(_OrderedEnum):
    """
    Enumeration representing the scope of a `DataNode^` among the following values : `GLOBAL`, `CYCLE`, `SCENARIO`,
    `PIPELINE`.
    """

    GLOBAL = 4
    CYCLE = 3
    SCENARIO = 2
    PIPELINE = 1
