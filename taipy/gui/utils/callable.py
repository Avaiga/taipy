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
from inspect import isclass
from types import LambdaType


def _is_function(s: t.Any) -> bool:
    return callable(s) and not isclass(s)


def _function_name(s: t.Any) -> str:
    if hasattr(s, "__name__"):
        return s.__name__
    elif callable(s):
        return f"<instance of {type(s).__name__}>"
    else:
        return str(s)


def _is_unnamed_function(s: t.Any):
    return isinstance(s, LambdaType) or (callable(s) and not hasattr(s, "__name__"))
