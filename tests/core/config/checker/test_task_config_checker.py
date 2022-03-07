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
