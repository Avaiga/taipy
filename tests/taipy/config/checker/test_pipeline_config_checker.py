from taipy.config._config import _Config
from taipy.config.checker.checkers.pipeline_config_checker import PipelineConfigChecker
from taipy.config.checker.issue_collector import IssueCollector
from taipy.config.task_config import TaskConfig


class TestPipelineConfigChecker:
    def test_check_task(self):
        collector = IssueCollector()
        config = _Config.default_config()
        PipelineConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config.pipelines["default"].tasks = [TaskConfig("bar")]
        collector = IssueCollector()
        PipelineConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config.pipelines["default"].tasks = "bar"
        collector = IssueCollector()
        PipelineConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0

        config.pipelines["default"].tasks = ["bar"]
        collector = IssueCollector()
        PipelineConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 0
