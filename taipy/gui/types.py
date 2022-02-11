from enum import Enum
import typing as t

from .utils import (
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
    data = "data"
    date = "date"
    lov_value = "lovvalue"
    lov = "lov"
    content = "content"
    image = "image"


def _get_taipy_type(a_type: t.Optional[AttributeType]) -> t.Optional[str]:
    if a_type == AttributeType.data:
        return TaipyData.__name__
    elif a_type == AttributeType.boolean or a_type == AttributeType.dynamic_boolean:
        return TaipyBool.__name__
    elif a_type == AttributeType.number or a_type == AttributeType.dynamic_number:
        return TaipyNumber.__name__
    elif a_type == AttributeType.date:
        return TaipyDate.__name__
    elif a_type == AttributeType.lov_value:
        return TaipyLovValue.__name__
    elif a_type == AttributeType.lov:
        return TaipyLov.__name__
    elif a_type == AttributeType.content:
        return TaipyContent.__name__
    elif a_type == AttributeType.image:
        return TaipyContentImage.__name__
    return None
