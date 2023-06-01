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

from taipy.config._config import _Config
from taipy.config.checker._checkers._global_config_checker import _GlobalConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.global_app.global_app_config import GlobalAppConfig


def test_check_repository_type_value_filesystem():
    config = _Config()
    config._global_config.repository_type = "filesystem"
    collector = IssueCollector()
    _GlobalConfigChecker(config, collector)._check()
    assert len(collector.warnings) == 0


def test_check_repository_type_value_sql():
    config = _Config()
    config._global_config.repository_type = "sql"
    collector = IssueCollector()
    _GlobalConfigChecker(config, collector)._check()
    assert len(collector.warnings) == 0


def test_check_repository_type_value_wrong_str():
    config = _Config()
    config._global_config.clean_entities_enabled = False
    config._global_config.repository_type = "any"
    collector = IssueCollector()
    _GlobalConfigChecker(config, collector)._check()
    assert len(collector.warnings) == 1
    assert collector.warnings[0].field == GlobalAppConfig._REPOSITORY_TYPE_KEY
    assert collector.warnings[0].value == "any"
