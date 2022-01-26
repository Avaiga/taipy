from taipy.config._config import _Config
from taipy.config.checker import IssueCollector
from taipy.config.checker.checkers.data_node_config_checker import DataNodeConfigChecker
from taipy.data.scope import Scope


class TestDataNodeConfigChecker:
    def test_check_storage_type(self):
        collector = IssueCollector()
        config = _Config.default_config()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].storage_type = "bar"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_nodes["default"].storage_type = "csv"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_nodes["default"].storage_type = "sql"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 6

        config.data_nodes["default"].storage_type = "excel"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_nodes["default"].storage_type = "pickle"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].storage_type = "in_memory"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

    def test_check_scope(self):
        config = _Config.default_config()

        config.data_nodes["default"].scope = "bar"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_nodes["default"].scope = 1
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_nodes["default"].scope = Scope.GLOBAL
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].scope = Scope.BUSINESS_CYCLE
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].scope = Scope.SCENARIO
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].scope = Scope.PIPELINE
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

    def test_check_required_properties(self):
        config = _Config.default_config()

        config.data_nodes["default"].storage_type = "csv"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_nodes["default"].storage_type = "csv"
        config.data_nodes["default"].properties = {"has_header": True}
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_nodes["default"].storage_type = "csv"
        config.data_nodes["default"].properties = {"has_header": True, "path": "bar"}
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].storage_type = "sql"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 6

        required_properties = ["db_username", "db_password", "db_name", "db_engine", "read_query", "write_table"]
        config.data_nodes["default"].storage_type = "sql"
        config.data_nodes["default"].properties = {key: "" for key in required_properties}
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].storage_type = "excel"
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_nodes["default"].storage_type = "excel"
        config.data_nodes["default"].properties = {"has_header": True}
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_nodes["default"].storage_type = "excel"
        config.data_nodes["default"].properties = {"has_header": True, "path": "bar"}
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_nodes["default"].storage_type = "excel"
        config.data_nodes["default"].properties = {
            "has_header": True,
            "path": "bar",
            "sheet_name": ["sheet_name_1", "sheet_name_2"],
        }
        collector = IssueCollector()
        DataNodeConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
