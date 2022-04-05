# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import os
from unittest import mock

from taipy.core.config._config import _Config
from taipy.core.config.checker._checkers._gLobal_config_checker import _GlobalConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.global_app_config import GlobalAppConfig


class TestGlobalConfigChecker:
    def test_check_boolean_field_is_bool(self):
        collector = IssueCollector()
        config = _Config()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert collector.errors[0].field == GlobalAppConfig._CLEAN_ENTITIES_ENABLED_KEY
        assert collector.errors[0].value is None

        config._global_config.clean_entities_enabled = True
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0

        config._global_config.clean_entities_enabled = False
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0

        config._global_config.clean_entities_enabled = "foo"
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1

        config._global_config.clean_entities_enabled = GlobalAppConfig._CLEAN_ENTITIES_ENABLED_TEMPLATE
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0

        with mock.patch.dict(os.environ, {"FOO": "true"}):
            config._global_config.clean_entities_enabled = "ENV[FOO]"
            collector = IssueCollector()
            _GlobalConfigChecker(config, collector)._check()
            assert len(collector.errors) == 0

        with mock.patch.dict(os.environ, {"FOO": "foo"}):
            config._global_config.clean_entities_enabled = "ENV[FOO]"
            collector = IssueCollector()
            _GlobalConfigChecker(config, collector)._check()
            assert len(collector.errors) == 1
