from enum import Enum


class WsType(Enum):
    UPDATE = "U"
    MULTIPLE_UPDATE = "MU"
    ACTION = "A"
    TABLE_UPDATE = "T"
    REQUEST_UPDATE = "RU"


NumberTypes = set(["int", "int64", "float", "float64"])


class AttributeType(Enum):
    string = "string"
    number = "number"
    boolean = "boolean"
    json = "json"
    react = "react"
