from enum import Enum


class Scope(Enum):
    """
    Class to represent the scope of usage of a Data Source
    """

    GLOBAL = 1
    TIME_BUCKET = 2
    SCENARIO = 3
    PIPELINE = 4
