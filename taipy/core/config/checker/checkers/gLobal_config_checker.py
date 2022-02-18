from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.config_checker import ConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.global_app_config import GlobalAppConfig


class GlobalConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def check(self) -> IssueCollector:
        global_config = self.config.global_config
        self._check_notification_field(global_config)
        return self.collector

    def _check_notification_field(self, global_config: GlobalAppConfig):
        if not isinstance(global_config.notification, bool):
            self._error(
                global_config.NOTIFICATION_KEY,
                global_config.notification,
                f"{global_config.NOTIFICATION_KEY} field must be populated with a boolean value.",
            )
