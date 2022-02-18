from copy import copy

from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.task_config_checker import TaskConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.data_node_config import DataNodeConfig


class TestTaskConfigChecker:
    def test_check_config_name(self):
        config = _Config.default_config()
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config.tasks["new"] = copy(config.tasks["default"])
        config.tasks["new"].name = None
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 2
        assert len(collector.warnings) == 2

        config.tasks["new"].name = "new"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

    def test_check_inputs(self):
        config = _Config.default_config()
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config.tasks["new"] = config.tasks["default"]
        config.tasks["new"].name, config.tasks["new"].function = "new", print
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2

        config.tasks["new"].inputs = "bar"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config.tasks["new"].inputs = ["bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config.tasks["new"].inputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config.tasks["new"].inputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

    def test_check_outputs(self):
        config = _Config.default_config()

        config.tasks["default"].outputs = "bar"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config.tasks["new"] = config.tasks["default"]
        config.tasks["new"].name, config.tasks["new"].function = "new", print
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config.tasks["new"].outputs = ["bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

        config.tasks["new"].outputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 1

        config.tasks["new"].outputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 1

    def test_check_function(self):
        def mock_func():
            pass

        config = _Config.default_config()

        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 0

        config.tasks["new"] = copy(config.tasks["default"])
        config.tasks["new"].name = "new"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["new"].function = None
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["new"].function = "bar"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["new"].function = mock_func
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2
