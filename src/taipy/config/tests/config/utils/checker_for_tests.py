from src.taipy.config import IssueCollector
from src.taipy.config.checker._checkers._config_checker import _ConfigChecker


class CheckerForTest(_ConfigChecker):

    def _check(self) -> IssueCollector:
        return self._collector
