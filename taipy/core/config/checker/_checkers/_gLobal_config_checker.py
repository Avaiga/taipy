from taipy.core.config._config import _Config
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as tpl
from taipy.core.config.checker._checkers._config_checker import _ConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.global_app_config import GlobalAppConfig
from taipy.core.exceptions.exceptions import InconsistentEnvVariableError


class _GlobalConfigChecker(_ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def _check(self) -> IssueCollector:
        global_config = self._config._global_config
        self._check_clean_entities_enabled_type(global_config)
        return self._collector

    def _check_clean_entities_enabled_type(self, global_config: GlobalAppConfig):
        value = global_config.clean_entities_enabled

        if isinstance(global_config.clean_entities_enabled, str):
            try:
                value = tpl._replace_templates(
                    global_config.clean_entities_enabled,
                    type=bool,
                    required=False,
                    default=GlobalAppConfig._DEFAULT_CLEAN_ENTITIES_ENABLED,
                )
            except InconsistentEnvVariableError:
                pass
        if isinstance(value, bool):
            return
        self._error(
            global_config._CLEAN_ENTITIES_ENABLED_KEY,
            value,
            f"{global_config._CLEAN_ENTITIES_ENABLED_KEY} field must be populated with a boolean value.",
        )
