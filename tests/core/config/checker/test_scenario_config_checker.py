from copy import copy

from taipy.core.common.frequency import Frequency
from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.scenario_config_checker import ScenarioConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.pipeline_config import PipelineConfig


class TestScenarioConfigChecker:
    def test_check_config_name(self):
        collector = IssueCollector()
        config = _Config.default_config()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config.scenarios["new"] = copy(config.scenarios["default"])
        config.scenarios["new"].name = None
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config.scenarios["new"].name = "new"
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

    def test_check_pipelines(self):
        collector = IssueCollector()
        config = _Config.default_config()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config.scenarios["new"] = copy(config.scenarios["default"])
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config.scenarios["new"].pipelines = "bar"
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

        config.scenarios["new"].pipelines = ["bar"]
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

        config.scenarios["new"].pipelines = ["bar", PipelineConfig("bar")]
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

        config.scenarios["new"].pipelines = [PipelineConfig("bar")]
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 1

    def test_check_frequency(self):
        config = _Config.default_config()

        config.scenarios["default"].frequency = "bar"
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config.scenarios["new"] = copy(config.scenarios["default"])
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config.scenarios["new"].frequency = 1
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config.scenarios["new"].frequency = Frequency.DAILY
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

    def test_check_comparators(self):
        config = _Config.default_config()

        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0
        assert len(collector.infos) == 0

        config.scenarios["new"] = copy(config.scenarios["default"])
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 1

        config.scenarios["new"].comparators = {"bar": "abc"}
        collector = IssueCollector()
        ScenarioConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1
        assert len(collector.infos) == 0
