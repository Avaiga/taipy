from taipy.common.repr_enum import ReprEnum


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
    The scope of usage of a Data Node.
    """

    GLOBAL = 4
    BUSINESS_CYCLE = 3
    SCENARIO = 2
    PIPELINE = 1
