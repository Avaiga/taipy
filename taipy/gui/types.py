from enum import Enum
import typing as t

from .utils import (
    TaipyBase,
    TaipyBool,
    TaipyContent,
    TaipyContentImage,
    TaipyData,
    TaipyDate,
    TaipyLov,
    TaipyLovValue,
    TaipyNumber,
)


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
    boolean = "boolean"
    content = TaipyContent
    data = TaipyData
    date = TaipyDate
    dict = "dict"
    dynamic_number = TaipyNumber
    dynamic_boolean = TaipyBool
    dynamic_list = "dynamiclist"
    function = "function"
    image = TaipyContentImage
    json = "json"
    lov = TaipyLov
    lov_value = TaipyLovValue
    number = "number"
    react = "react"
    string = "string"
    string_or_number = "string|number"


def _get_taipy_type(a_type: t.Optional[AttributeType]) -> t.Optional[t.Type[TaipyBase]]:
    if isinstance(a_type, AttributeType) and isinstance(a_type.value, TaipyBase.__class__):
        return a_type.value
    if a_type == AttributeType.boolean:
        return TaipyBool
    elif a_type == AttributeType.number:
        return TaipyNumber
    return None
