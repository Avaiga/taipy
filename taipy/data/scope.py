from enum import Enum


class Scope(Enum):
    """
    Class to represent the scope of usage of a Data Source
    """

    GLOBAL = 4
    TIME_BUCKET = 3
    SCENARIO = 2
    PIPELINE = 1
