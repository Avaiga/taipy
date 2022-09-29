# Copyright 2022 Avaiga Private Limited
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

from .data import Decimator
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
    ACKNOWLEDGEMENT = "ACK"


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
    content = _TaipyContent
    data = _TaipyData
    date = _TaipyDate
    dict = "dict"
    """
    The property holds a dictionary.
    """
    dynamic_number = _TaipyNumber
    """
    The property holds a dynamic number.
    """
    dynamic_boolean = _TaipyBool
    """
    The property holds a dynamic Boolean value.
    """
    dynamic_list = "dynamiclist"
    dynamic_string = "dynamicstring"
    """
    The property holds a dynamic string.
    """
    function = "function"
    """
    The property holds a reference to a function.
    """
    image = _TaipyContentImage
    json = "json"
    lov = _TaipyLov
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
    number_or_lov_value = "number|lovValue"
    string_list = "stringlist"
    decimator = Decimator


def _get_taipy_type(a_type: t.Optional[PropertyType]) -> t.Optional[t.Type[_TaipyBase]]:
    if isinstance(a_type, PropertyType) and not isinstance(a_type.value, str):
        return a_type.value
    if a_type == PropertyType.boolean:
        return _TaipyBool
    elif a_type == PropertyType.number:
        return _TaipyNumber
    return None
