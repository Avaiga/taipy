from taipy.core.common.repr_enum import ReprEnum


class OrderedEnum(ReprEnum):
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


class Scope(OrderedEnum):
    """
    The scope of a Data Node among the following values : GLOBAL, CYCLE, SCENARIO, PIPELINE
    """

    GLOBAL = 4
    CYCLE = 3
    SCENARIO = 2
    PIPELINE = 1
