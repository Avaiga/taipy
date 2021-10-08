from enum import Enum


class WsType(Enum):
    UPDATE = "U"
    MULTIPLE_UPDATE = "MU"
    ACTION = "A"
    TABLE_UPDATE = "T"
