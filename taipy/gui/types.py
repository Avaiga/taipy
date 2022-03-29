import typing as t
from enum import Enum

from .utils import (
    _TaipyBase,
    _TaipyBool,
    _TaipyContent,
    _TaipyContentImage,
    _TaipyData,
    _TaipyDate,
    _TaipyLov,
    _TaipyLovValue,
    _TaipyNumber,
)


class _WsType(Enum):
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
    DOWNLOAD_FILE = "DF"
    PARTIAL = "PR"


NumberTypes = {"int", "int64", "float", "float64"}


class _AttributeType(Enum):
    boolean = "boolean"
    content = _TaipyContent
    data = _TaipyData
    date = _TaipyDate
    dict = "dict"
    dynamic_number = _TaipyNumber
    dynamic_boolean = _TaipyBool
    dynamic_list = "dynamiclist"
    dynamic_string = "dynamicstring"
    function = "function"
    image = _TaipyContentImage
    json = "json"
    lov = _TaipyLov
    lov_value = _TaipyLovValue
    number = "number"
    react = "react"
    string = "string"
    string_or_number = "string|number"
    boolean_or_list = "boolean|list"
    number_or_lov_value = "number|lovValue"


def _get_taipy_type(a_type: t.Optional[_AttributeType]) -> t.Optional[t.Type[_TaipyBase]]:
    if isinstance(a_type, _AttributeType) and not isinstance(a_type.value, str):
        return a_type.value
    if a_type == _AttributeType.boolean:
        return _TaipyBool
    elif a_type == _AttributeType.number:
        return _TaipyNumber
    return None
