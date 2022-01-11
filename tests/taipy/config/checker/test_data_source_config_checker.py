from taipy.config import Config
from taipy.config._config import _Config
from taipy.config.checker import IssueCollector
from taipy.config.checker.checkers.data_source_config_checker import DataSourceConfigChecker
from taipy.config.data_source_config import DataSourceConfig
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
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "sql"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "pickle"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.data_sources["default"].storage_type = "in_memory"
        collector = IssueCollector()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

    def test_check_scope(self):
        collector = IssueCollector()
        config = _Config.default_config()
        DataSourceConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

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
