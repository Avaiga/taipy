from taipy.config._config import _Config
from taipy.config.checker import IssueCollector
from taipy.config.checker.checkers.task_config_checker import TaskConfigChecker
from taipy.config.data_node_config import DataNodeConfig


class TestTaskConfigChecker:
    def test_check_inputs(self):
        collector = IssueCollector()
        config = _Config.default_config()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 3

        config.tasks["default"].inputs = "bar"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["default"].inputs = ["bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["default"].inputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2

        config.tasks["default"].inputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

    def test_check_outputs(self):
        config = _Config.default_config()

        config.tasks["default"].outputs = "bar"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["default"].outputs = [DataNodeConfig("bar")]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2

        config.tasks["default"].outputs = [DataNodeConfig("bar"), "bar"]
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

    def test_check_function(self):
        def mock_func():
            pass

        config = _Config.default_config()

        config.tasks["default"].function = "bar"
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert len(collector.warnings) == 2

        config.tasks["default"].function = mock_func
        collector = IssueCollector()
        TaskConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
        assert len(collector.warnings) == 2
