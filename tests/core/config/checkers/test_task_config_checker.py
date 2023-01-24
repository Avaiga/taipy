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

from copy import copy

from src.taipy.core.config import TaskConfig
from src.taipy.core.config.checkers._task_config_checker import _TaskConfigChecker
from src.taipy.core.config.data_node_config import DataNodeConfig
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.config import Config


class TestTaskConfigChecker:
    def test_check_config_id(self):
        config = Config._default_config
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"].id = None
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 2
        assert len(collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].id = "new"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

    def test_check_inputs(self):
        config = Config._default_config
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = config._sections[TaskConfig.name]["default"]
        config._sections[TaskConfig.name]["new"].id, config._sections[TaskConfig.name]["new"].function = "new", print
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2

        config._sections[TaskConfig.name]["new"]._inputs = "bar"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._inputs = ["bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._inputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._inputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

    def test_check_outputs(self):
        config = Config._default_config

        config._sections[TaskConfig.name]["default"]._outputs = "bar"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = config._sections[TaskConfig.name]["default"]
        config._sections[TaskConfig.name]["new"].id, config._sections[TaskConfig.name]["new"].function = "new", print
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._outputs = ["bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._outputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config._sections[TaskConfig.name]["new"]._outputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

    def test_check_function(self):
        def mock_func():
            pass

        config = Config._default_config

        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._sections[TaskConfig.name]["new"] = copy(config._sections[TaskConfig.name]["default"])
        config._sections[TaskConfig.name]["new"].id = "new"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].function = None
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].function = "bar"
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config._sections[TaskConfig.name]["new"].function = mock_func
        collector = IssueCollector()
        _TaskConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2
