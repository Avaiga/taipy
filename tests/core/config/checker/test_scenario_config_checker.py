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

from taipy.core.common.frequency import Frequency
from taipy.core.config._config import _Config
from taipy.core.config.checker._checkers._scenario_config_checker import _ScenarioConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.pipeline_config import PipelineConfig


class TestScenarioConfigChecker:
    def test_check_config_id(self):
        collector = IssueCollector()
        config = _Config._default_config()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config._scenarios["new"] = copy(config._scenarios["default"])
        config._scenarios["new"].id = None
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config._scenarios["new"].id = "new"
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

    def test_check_pipelines(self):
        collector = IssueCollector()
        config = _Config._default_config()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config._scenarios["new"] = copy(config._scenarios["default"])
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config._scenarios["new"]._pipelines = "bar"
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

        config._scenarios["new"]._pipelines = ["bar"]
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

        config._scenarios["new"]._pipelines = ["bar", PipelineConfig("bar")]
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

        config._scenarios["new"]._pipelines = [PipelineConfig("bar")]
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

    def test_check_frequency(self):
        config = _Config._default_config()

        config._scenarios["default"].frequency = "bar"
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config._scenarios["new"] = copy(config._scenarios["default"])
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config._scenarios["new"].frequency = 1
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config._scenarios["new"].frequency = Frequency.DAILY
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

    def test_check_comparators(self):
        config = _Config._default_config()

        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config._scenarios["new"] = copy(config._scenarios["default"])
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config._scenarios["new"].comparators = {"bar": "abc"}
        collector = IssueCollector()
        _ScenarioConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 0
