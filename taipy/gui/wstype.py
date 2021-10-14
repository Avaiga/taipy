from enum import Enum


class WsType(Enum):
    ACTION = "A"
    CHART_UPDATE = "CU"
    MULTIPLE_UPDATE = "MU"
    REQUEST_UPDATE = "RU"
    TABLE_UPDATE = "T"
    UPDATE = "U"


NumberTypes = set(["int", "int64", "float", "float64"])


class AttributeType(Enum):
    string = "string"
    number = "number"
    string_or_number = "string|number"
    boolean = "boolean"
    json = "json"
    react = "react"
