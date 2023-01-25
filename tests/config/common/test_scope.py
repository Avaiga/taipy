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

import pytest

from src.taipy.config.common.scope import Scope


def test_scope():
    # Test __ge__ method
    assert Scope.SCENARIO >= Scope.PIPELINE
    assert Scope.SCENARIO >= Scope.SCENARIO
    assert Scope.PIPELINE >= Scope.PIPELINE
    with pytest.raises(TypeError):
        assert Scope.PIPELINE >= "testing string"

    # Test __gt__ method
    assert Scope.GLOBAL > Scope.PIPELINE
    assert Scope.GLOBAL > Scope.SCENARIO
    assert Scope.GLOBAL > Scope.PIPELINE
    with pytest.raises(TypeError):
        assert Scope.PIPELINE > "testing string"

    # Test __le__ method
    assert Scope.PIPELINE <= Scope.SCENARIO
    assert Scope.PIPELINE <= Scope.PIPELINE
    assert Scope.PIPELINE <= Scope.SCENARIO
    with pytest.raises(TypeError):
        assert Scope.PIPELINE <= "testing string"

    # Test __lt__ method
    assert Scope.PIPELINE < Scope.SCENARIO
    assert Scope.PIPELINE < Scope.SCENARIO
    assert Scope.SCENARIO < Scope.GLOBAL
    with pytest.raises(TypeError):
        assert Scope.PIPELINE < "testing string"
