from taipy.config._config import _Config
from taipy.config.checker.checker import Checker


class TestDefaultConfigChecker:
    def test_check_default_config(self):
        config = _Config.default_config()
        collector = Checker().check(config)
        assert len(collector.all) == 0
