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
    string_list = "stringlist"


def _get_taipy_type(a_type: t.Optional[_AttributeType]) -> t.Optional[t.Type[_TaipyBase]]:
    if isinstance(a_type, _AttributeType) and not isinstance(a_type.value, str):
        return a_type.value
    if a_type == _AttributeType.boolean:
        return _TaipyBool
    elif a_type == _AttributeType.number:
        return _TaipyNumber
    return None
