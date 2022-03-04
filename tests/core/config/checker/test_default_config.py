from taipy.core.config._config import _Config
from taipy.core.config.checker.checker import Checker


class TestDefaultConfigChecker:
    def test_check_default_config(self):
        config = _Config.default_config()
        collector = Checker().check(config)
        assert len(collector._errors) == 0
        assert len(collector._infos) == 0
        assert len(collector._warnings) == 0
