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

from taipy.common.config import Config
from taipy.common.config.checker.issue_collector import IssueCollector
from taipy.core.config.checkers._core_section_checker import _CoreSectionChecker
from taipy.core.config.core_section import CoreSection


class TestCoreSectionChecker:
    _CoreSectionChecker._ACCEPTED_REPOSITORY_TYPES.update(["mock_repo_type"])

    def test_check_valid_repository(self):
        Config.configure_core(repository_type="mock_repo_type")
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 0

        Config.configure_core(repository_type="filesystem")
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 0

        Config.configure_core(repository_type="sql")
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 0

        Config.configure_core(repository_type="filesystem")

    def test_check_repository_type_value_wrong_str(self):
        Config.configure_core(repository_type="any")
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 1
        assert Config._collector.warnings[0].field == CoreSection._REPOSITORY_TYPE_KEY
        assert Config._collector.warnings[0].value == "any"

    def test_check_repository_type_value_wrong_type(self):
        Config.configure_core(repository_type=1)
        Config._collector = IssueCollector()
        Config.check()
        assert len(Config._collector.warnings) == 1
        assert Config._collector.warnings[0].field == CoreSection._REPOSITORY_TYPE_KEY
        assert Config._collector.warnings[0].value == 1
