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

import os
from unittest import mock

from src.taipy.config._config import _Config
from src.taipy.config.checker._checkers._global_config_checker import _GlobalConfigChecker
from src.taipy.config.checker.issue_collector import IssueCollector
from src.taipy.config.global_app.global_app_config import GlobalAppConfig


class TestGlobalConfigChecker:

    _GlobalConfigChecker._ACCEPTED_REPOSITORY_TYPES.update(["mock_repo_type"])

    def test_check_repository_type_mock_value_for_expansion(self):
        config = _Config()
        config._global_config.repository_type = "mock_repo_type"
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.warnings) == 0

    def test_check_repository_type_value_filesystem(self):
        config = _Config()
        config._global_config.repository_type = "filesystem"
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.warnings) == 0

    def test_check_repository_type_value_wrong_str(self):
        config = _Config()
        config._global_config.repository_type = "any"
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.warnings) == 1
        assert collector.warnings[0].field == GlobalAppConfig._REPOSITORY_TYPE_KEY
        assert collector.warnings[0].value == "any"

    def test_check_repository_type_value_wrong_type(self):
        config = _Config()
        config._global_config.repository_type = 1
        collector = IssueCollector()
        _GlobalConfigChecker(config, collector)._check()
        assert len(collector.warnings) == 1
        assert collector.warnings[0].field == GlobalAppConfig._REPOSITORY_TYPE_KEY
        assert collector.warnings[0].value == 1
