# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import re

import pandas as pd


def _get_data_type(value):
    if pd.api.types.is_bool_dtype(value):
        return "bool"
    elif pd.api.types.is_integer_dtype(value):
        return "int"
    elif pd.api.types.is_float_dtype(value):
        return "float"
    return re.match(r"^<class '(.*\.)?(.*?)(\d\d)?'>", str(type(value))).group(2)
