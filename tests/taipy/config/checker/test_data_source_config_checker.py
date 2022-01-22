from taipy.config._config import _Config
from taipy.config.checker import IssueCollector
from taipy.config.checker.checkers.data_source_config_checker import DataSourceConfigChecker
from taipy.data.scope import Scope


class TestDataSourceConfigChecker:
    def test_check_storage_type(self):
        collector = IssueCollector()
        config = _Config.default_config()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "bar"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_sources["default"].storage_type = "csv"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_sources["default"].storage_type = "sql"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 6

        config.data_sources["default"].storage_type = "excel"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_sources["default"].storage_type = "pickle"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "in_memory"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

    def test_check_scope(self):
        config = _Config.default_config()

        config.data_sources["default"].scope = "bar"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_sources["default"].scope = 1
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_sources["default"].scope = Scope.GLOBAL
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].scope = Scope.BUSINESS_CYCLE
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].scope = Scope.SCENARIO
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].scope = Scope.PIPELINE
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

    def test_check_required_properties(self):
        config = _Config.default_config()

        config.data_sources["default"].storage_type = "csv"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_sources["default"].storage_type = "csv"
        config.data_sources["default"].properties = {"has_header": True}
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_sources["default"].storage_type = "csv"
        config.data_sources["default"].properties = {"has_header": True, "path": "bar"}
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "sql"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 6

        required_properties = ["db_username", "db_password", "db_name", "db_engine", "read_query", "write_table"]
        config.data_sources["default"].storage_type = "sql"
        config.data_sources["default"].properties = {key: "" for key in required_properties}
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "excel"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 2

        config.data_sources["default"].storage_type = "excel"
        config.data_sources["default"].properties = {"has_header": True}
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 1

        config.data_sources["default"].storage_type = "excel"
        config.data_sources["default"].properties = {"has_header": True, "path": "bar"}
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "excel"
        config.data_sources["default"].properties = {
            "has_header": True,
            "path": "bar",
            "sheet_name": ["sheet_name_1", "sheet_name_2"],
        }
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
