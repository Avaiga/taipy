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

import functools
from collections import namedtuple
from importlib import import_module
from operator import attrgetter
from typing import Callable, Optional


@functools.lru_cache
def _load_fct(module_name: str, fct_name: str) -> Callable:
    module = import_module(module_name)
    return attrgetter(fct_name)(module)


@functools.lru_cache
def _get_fct_name(f) -> Optional[str]:
    # Mock function does not have __qualname__ attribute -> return __name__
    # Partial or anonymous function does not have __name__ or __qualname__ attribute -> return None
    name = getattr(f, "__qualname__", getattr(f, "__name__", None))
    return name


def _fct_to_dict(obj):
    params = []
    callback = obj

    if isinstance(obj, _Subscriber):
        callback = obj.callback
        params = obj.params

    fct_name = _get_fct_name(callback)
    if not fct_name:
        return None
    return {
        "fct_name": fct_name,
        "fct_params": params,
        "fct_module": callback.__module__,
    }


def _fcts_to_dict(objs):
    return [d for obj in objs if (d := _fct_to_dict(obj)) is not None]


_Subscriber = namedtuple("_Subscriber", "callback params")
