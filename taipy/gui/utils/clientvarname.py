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

_replace_dict = {".": "__", "[": "_SqrOp_", "]": "_SqrCl_"}


def _get_client_var_name(var_name: str) -> str:
    for k, v in _replace_dict.items():
        var_name = var_name.replace(k, v)
    return var_name


def _to_camel_case(value: str, upcase_first=False) -> str:
    if not isinstance(value, str):
        raise Exception("_to_camel_case allows only string parameter")

    if len(value) <= 1:
        return value.lower()
    value = value.replace("_", " ").title().replace(" ", "").replace("[", "_").replace("]", "_")
    return value[0].lower() + value[1:] if not upcase_first else value


def _get_broadcast_var_name(s: str) -> str:
    return _get_client_var_name(f"_bc_{s}")
