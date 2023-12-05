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
from taipy.config.common._validate_id import _validate_id
from taipy.config.exceptions.exceptions import InvalidConfigurationId


class TestId:
    def test_validate_id(self):
        s = _validate_id("foo")
        assert s == "foo"
        with pytest.raises(InvalidConfigurationId):
            _validate_id("1foo")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("foo bar")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("foo/foo$")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("")
        with pytest.raises(InvalidConfigurationId):
            _validate_id(" ")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("class")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("def")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("with")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("CYCLE")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("SCENARIO")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("SEQUENCE")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("TASK")
        with pytest.raises(InvalidConfigurationId):
            _validate_id("DATANODE")
