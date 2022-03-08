from taipy.core.config._config import _Config
from taipy.core.config.checker._checkers._config_checker import _ConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.global_app_config import GlobalAppConfig


class _GlobalConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        global_config = self._config._global_config
        self._check_bolean_field(global_config)
        return self._collector

    def _check_bolean_field(self, global_config: GlobalAppConfig):
        if not isinstance(global_config.clean_entities_enabled, bool):
            self._error(
                global_config._CLEAN_ENTITIES_ENABLED_KEY,
                global_config.clean_entities_enabled,
                f"{global_config._CLEAN_ENTITIES_ENABLED_KEY} field must be populated with a boolean value.",
            )
