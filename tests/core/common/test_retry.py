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

import pytest

from taipy.config import Config
from taipy.core.common._utils import _retry_read_entity
from taipy.core.exceptions import InvalidExposedType


def test_retry_decorator(mocker):
    func = mocker.Mock(side_effect=InvalidExposedType())

    @_retry_read_entity((InvalidExposedType,))
    def decorated_func():
        func()

    with pytest.raises(InvalidExposedType):
        decorated_func()
    # Called once in the normal flow and no retry
    # The Config.core.read_entity_retry is set to 0 at conftest.py
    assert Config.core.read_entity_retry == 0
    assert func.call_count == 1

    func.reset_mock()

    Config.core.read_entity_retry = 3
    with pytest.raises(InvalidExposedType):
        decorated_func()
    # Called once in the normal flow and 3 more times on the retry flow
    assert func.call_count == 4


def test_retry_decorator_exception_not_in_list(mocker):
    func = mocker.Mock(side_effect=KeyError())
    Config.core.read_entity_retry = 3

    @_retry_read_entity((InvalidExposedType,))
    def decorated_func():
        func()

    with pytest.raises(KeyError):
        decorated_func()
    # Called only on the first time and not trigger retry because KeyError is not on the exceptions list
    assert func.called == 1
