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

from functools import wraps
from importlib import util

from taipy.core.common._utils import _load_fct


def _middleware(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if _using_enterprise():
            return _enterprise_middleware()(f)(*args, **kwargs)
        else:
            return f(*args, **kwargs)

    return wrapper


def _using_enterprise():
    return util.find_spec("taipy.enterprise") is not None


def _enterprise_middleware():
    return _load_fct("taipy.enterprise.rest.api.middlewares._middleware", "_middleware")
