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

from copy import copy

from taipy.core.config._config import _Config
from taipy.core.config.checker._checkers._task_config_checker import _TaskConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.data_node_config import DataNodeConfig


class TestTaskConfigChecker:
    def test_check_config_id(self):
        config = _Config._default_config()
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._tasks["new"] = copy(config._tasks["default"])
        config._tasks["new"].id = None
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 2
        assert len(collector.warnings) == 2

        config._tasks["new"].id = "new"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

    def test_check_inputs(self):
        config = _Config._default_config()
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._tasks["new"] = config._tasks["default"]
        config._tasks["new"].id, config._tasks["new"].function = "new", print
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2

        config._tasks["new"]._inputs = "bar"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._tasks["new"]._inputs = ["bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._tasks["new"]._inputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config._tasks["new"]._inputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

    def test_check_outputs(self):
        config = _Config._default_config()

        config._tasks["default"]._outputs = "bar"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._tasks["new"] = config._tasks["default"]
        config._tasks["new"].id, config._tasks["new"].function = "new", print
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._tasks["new"]._outputs = ["bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._tasks["new"]._outputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config._tasks["new"]._outputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

    def test_check_function(self):
        def mock_func():
            pass

        config = _Config._default_config()

        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._tasks["new"] = copy(config._tasks["default"])
        config._tasks["new"].id = "new"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config._tasks["new"].function = None
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config._tasks["new"].function = "bar"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config._tasks["new"].function = mock_func
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2
