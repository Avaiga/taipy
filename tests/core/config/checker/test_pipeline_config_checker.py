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
from taipy.core.config.checker._checkers._pipeline_config_checker import _PipelineConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.task_config import TaskConfig


class TestPipelineConfigChecker:
    def test_check_config_id(self):
        collector = IssueCollector()
        config = _Config._default_config()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._pipelines["new"] = copy(config._pipelines["default"])
        config._pipelines["new"].id = None
        collector = IssueCollector()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config._pipelines["new"].id = "new"
        collector = IssueCollector()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

    def test_check_task(self):
        collector = IssueCollector()
        config = _Config._default_config()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._pipelines["new"] = copy(config._pipelines["default"])
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config._pipelines["new"].tasks = [TaskConfig("bar", None)]
        collector = IssueCollector()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config._pipelines["new"].tasks = "bar"
        collector = IssueCollector()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0

        config._pipelines["new"].tasks = ["bar"]
        collector = IssueCollector()
        _PipelineConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
