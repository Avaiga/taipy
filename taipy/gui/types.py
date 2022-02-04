from enum import Enum


class WsType(Enum):
    ACTION = "A"
    MULTIPLE_UPDATE = "MU"
    REQUEST_UPDATE = "RU"
    DATA_UPDATE = "DU"
    UPDATE = "U"
    ALERT = "AL"
    BLOCK = "BL"
    NAVIGATE = "NA"
    CLIENT_ID = "ID"
    MULTIPLE_MESSAGE = "MS"


NumberTypes = set(["int", "int64", "float", "float64"])


class AttributeType(Enum):
    string = "string"
    number = "number"
    string_or_number = "string|number"
    boolean = "boolean"
    json = "json"
    react = "react"
    dict = "dict"
    dynamic_number = "dynamicnumber"
    dynamic_boolean = "dynamicbool"
    dynamic_list = "dynamiclist"
