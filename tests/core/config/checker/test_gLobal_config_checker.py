from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.gLobal_config_checker import GlobalConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.global_app_config import GlobalAppConfig


class TestGlobalConfigChecker:
    def test_check_boolean_field_is_bool(self):
        collector = IssueCollector()
        config = _Config()
        GlobalConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
        assert collector.errors[0].field == GlobalAppConfig.CLEAN_ENTITIES_ENABLED_KEY
        assert collector.errors[0].value is None

        config.global_config.clean_entities_enabled = True
        collector = IssueCollector()
        GlobalConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        config.global_config.clean_entities_enabled = False
        collector = IssueCollector()
        GlobalConfigChecker(config, collector).check()
        assert len(collector.errors) == 0
