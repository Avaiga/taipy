# Copyright 2021-2025 Avaiga Private Limited
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
    _TaipyTime,
    _TaipyToJson,
    _TaipyToJsonable,
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
    GUI_ADDR = "GA"
    MULTIPLE_MESSAGE = "MS"
    DOWNLOAD_FILE = "DF"
    PARTIAL = "PR"
    ACKNOWLEDGEMENT = "ACK"
    FAVICON = "FV"
    BROADCAST = "BC"
    LOCAL_STORAGE = "LS"
    PATCH = "PT"


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
    dynamic_boolean = _TaipyBool
    """
    The property is dynamic and holds a Boolean value.
    """
    number = "number"
    """
    The property holds a number.
    """
    dynamic_number = _TaipyNumber
    """
    The property is dynamic and holds a number.
    """
    string = "string"
    """
    The property holds a string.
    """
    dynamic_string = "dynamicstring"
    """
    The property is dynamic and holds a string.
    """
    string_or_number = "string|number"
    """
    The property holds a string or a number.

    This is typically used to handle CSS dimension values, where a unit can be used.
    """
    date = _TaipyDate
    """
    The property holds a date.
    """
    time = _TaipyTime
    dynamic_date = "dynamicdate"
    """
    The property is dynamic and holds a date.
    """
    date_range = _TaipyDateRange
    dict = "dict"
    """
    The property holds a dictionary.
    """
    dynamic_dict = _TaipyDict
    """
    The property is dynamic and holds a dictionary.
    """
    toHtmlContent = _TaipyContentHtml
    content = _TaipyContent
    data = _TaipyData
    dynamic_lo_numbers = _TaipyLoNumbers
    """
    The property is dynamic and holds a list of numbers.
    """
    dynamic_list = "dynamiclist"
    """
    The property is dynamic and holds a list.

    The React component must have two parameters: "<propertyName>" that must be a list of object, and
    "default<PropertyName>" that must be a string, set to the JSON representation of the initial value
    of the property.
    """
    function = "function"
    """
    The property holds a reference to a function.
    """
    image = _TaipyContentImage
    json = _TaipyToJson
    """
    The property value is a JSON representation of the value and dynamic.

    Although dynamic, the implementation of a *json* property does not need the React component to
    have a "default<PropertyName>" parameter, as the JSON value is directly passed to the component
    and not used to set an initial value.
    """
    jsonable = _TaipyToJsonable
    """
    The property value is JSON serializable and dynamic.

    Although dynamic, the implementation of a *jsonable* property does not need the React component
    to have a "default<PropertyName>" parameter, as the JSON value is directly passed to the
    component and not used to set an initial value.
    """
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
    react = "react"
    broadcast = "broadcast"
    boolean_or_list = "boolean|list"
    slider_value = "number|number[]|lovValue"
    toggle_value = "boolean|lovValue"
    string_list = "stringlist"
    decimator = Decimator
    """
    The property holds an inner attributes that is defined by a library and cannot be overridden by the user.
    """
    inner = "inner"


@t.overload  # noqa: F811
def _get_taipy_type(a_type: None) -> None: ...


@t.overload
def _get_taipy_type(a_type: t.Type[_TaipyBase]) -> t.Type[_TaipyBase]:  # noqa: F811
    ...


@t.overload
def _get_taipy_type(a_type: PropertyType) -> t.Type[_TaipyBase]:  # noqa: F811
    ...


@t.overload
def _get_taipy_type(  # noqa: F811
    a_type: t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType, None],
) -> t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType, None]: ...


def _get_taipy_type(  # noqa: F811
    a_type: t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType, None],
) -> t.Union[t.Type[_TaipyBase], t.Type[Decimator], PropertyType, None]:
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
