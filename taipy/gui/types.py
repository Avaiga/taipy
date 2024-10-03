# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import typing as t
from enum import Enum
from inspect import isclass

from .data import Decimator
from .utils import (
    _TaipyBase,
    _TaipyBool,
    _TaipyContent,
    _TaipyContentHtml,
    _TaipyContentImage,
    _TaipyData,
    _TaipyDate,
    _TaipyDateRange,
    _TaipyDict,
    _TaipyLoNumbers,
    _TaipyLov,
    _TaipyLovValue,
    _TaipyNumber,
    _TaipyToJson,
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
    APP_ID = "AID"
    MULTIPLE_MESSAGE = "MS"
    DOWNLOAD_FILE = "DF"
    PARTIAL = "PR"
    ACKNOWLEDGEMENT = "ACK"
    GET_MODULE_CONTEXT = "GMC"
    GET_DATA_TREE = "GDT"
    GET_ROUTES = "GR"
    FAVICON = "FV"
    BROADCAST = "BC"


NumberTypes = {"int", "int64", "float", "float64"}


class PropertyType(Enum):
    """
    All the possible element property types.

    This is used when creating custom visual elements, where you have
    to indicate the type of each property.

    Some types are 'dynamic', meaning that if the property value is modified, it
    is automatically handled by Taipy and propagated to the entire application.

    See `ElementProperty^` for more details.
    """

    boolean = "boolean"
    """
    The property holds a Boolean value.
    """
    toHtmlContent = _TaipyContentHtml
    content = _TaipyContent
    data = _TaipyData
    date = _TaipyDate
    date_range = _TaipyDateRange
    dict = "dict"
    """
    The property holds a dictionary.
    """
    dynamic_date = "dynamicdate"
    """
    The property is dynamic and holds a date.
    """
    dynamic_dict = _TaipyDict
    """
    The property is dynamic and holds a dictionary.
    """
    dynamic_number = _TaipyNumber
    """
    The property is dynamic and holds a number.
    """
    dynamic_lo_numbers = _TaipyLoNumbers
    """
    The property is dynamic and holds a list of numbers.
    """
    dynamic_boolean = _TaipyBool
    """
    The property is dynamic and holds a Boolean value.
    """
    dynamic_list = "dynamiclist"
    """
    The property is dynamic and holds a list.
    """
    dynamic_string = "dynamicstring"
    """
    The property is dynamic and holds a string.
    """
    function = "function"
    """
    The property holds a reference to a function.
    """
    image = _TaipyContentImage
    json = "json"
    single_lov = "singlelov"
    lov = _TaipyLov
    lov_no_default = "lovnodefault"
    """
    The property holds a LoV (list of values).
    """
    lov_value = _TaipyLovValue
    """
    The property holds a value in a LoV (list of values).
    """
    number = "number"
    """
    The property holds a number.
    """
    react = "react"
    broadcast = "broadcast"
    string = "string"
    """
    The property holds a string.
    """
    string_or_number = "string|number"
    """
    The property holds a string or a number.

    This is typically used to handle CSS dimension values, where a unit can be used.
    """
    boolean_or_list = "boolean|list"
    slider_value = "number|number[]|lovValue"
    toggle_value = "boolean|lovValue"
    string_list = "stringlist"
    decimator = Decimator
    """
    The property holds an inner attributes that is defined by a library and cannot be overridden by the user.
    """
    inner = "inner"
    to_json = _TaipyToJson


@t.overload  # noqa: F811
def _get_taipy_type(a_type: None) -> None:
    ...


@t.overload
def _get_taipy_type(a_type: t.Type[_TaipyBase]) -> t.Type[_TaipyBase]:  # noqa: F811
    ...


@t.overload
def _get_taipy_type(a_type: PropertyType) -> t.Type[_TaipyBase]:  # noqa: F811
    ...


@t.overload
def _get_taipy_type(  # noqa: F811
    a_type: t.Optional[t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType]],
) -> t.Optional[t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType]]:
    ...


def _get_taipy_type(  # noqa: F811
    a_type: t.Optional[t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType]],
) -> t.Optional[t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType]]:
    if a_type is None:
        return None
    if isinstance(a_type, PropertyType) and not isinstance(a_type.value, str):
        return a_type.value
    if isclass(a_type) and not isinstance(a_type, PropertyType) and issubclass(a_type, _TaipyBase):
        return a_type
    if a_type == PropertyType.boolean:
        return _TaipyBool
    elif a_type == PropertyType.number:
        return _TaipyNumber
    return None
