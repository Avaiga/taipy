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

import functools
import time
from collections import namedtuple
from importlib import import_module
from operator import attrgetter
from typing import Callable, Optional, Tuple

from taipy.common.config import Config


@functools.lru_cache
def _load_fct(module_name: str, fct_name: str) -> Callable:
    module = import_module(module_name)
    return attrgetter(fct_name)(module)


def _retry_repository_operation(exceptions: Tuple, sleep_time: float = 0.2):
    """
    Retries the wrapped function/method if the exceptions listed
    in ``exceptions`` are thrown.
    The number of retries is defined by Config.core.read_entity_retry.

    Parameters:
        exceptions (tuple): Tuple of exceptions that trigger a retry attempt.
        sleep_time (float): Time to sleep between retries.
    """

    def decorator(func):
        def newfn(*args, **kwargs):
            for _ in range(Config.core.read_entity_retry):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    time.sleep(sleep_time)
            return func(*args, **kwargs)

        return newfn

    return decorator


@functools.lru_cache
def _get_fct_name(f) -> Optional[str]:
    # Mock function does not have __qualname__ attribute -> return __name__
    # Partial or anonymous function does not have __name__ or __qualname__ attribute -> return None
    return getattr(f, "__qualname__", getattr(f, "__name__", None))


def _fct_to_dict(obj):
    params = []
    callback = obj

    if isinstance(obj, _Subscriber):
        callback = obj.callback
        params = obj.params

    if fct_name := _get_fct_name(callback):
        return {
            "fct_name": fct_name,
            "fct_params": params,
            "fct_module": callback.__module__,
        }

    return None


def _fcts_to_dict(objs):
    return [d for obj in objs if (d := _fct_to_dict(obj)) is not None]


_Subscriber = namedtuple("_Subscriber", "callback params")
