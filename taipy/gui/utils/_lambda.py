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
from types import LambdaType

from ._variable_directory import _variable_encode


def _get_lambda_id(lambda_fn: LambdaType, module: t.Optional[str] = None, index: t.Optional[int] = None):
    return _variable_encode(
        f"__lambda_{id(lambda_fn)}{f'_{index}' if index is not None else ''}", lambda_fn.__module__ or module
    )
