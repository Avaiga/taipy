import taipy.core.taipy as tp
from taipy.core.config.checker.checkers.job_config_checker import JobConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.config import Config
from taipy.core.config.job_config import JobConfig
from taipy.core.data.data_manager import DataManager


class TestJobConfigChecker:
    def test_check_multiprocess_mode(self):
        collector = IssueCollector()
        config = Config._python_config
        JobConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        dn_config_1 = Config.add_data_node(name="foo", storage_type="in_memory")
        DataManager.get_or_create(dn_config_1)
        assert len(tp.get_data_nodes()) == 1

        tp.configure_job_executions(mode=JobConfig.MODE_VALUE_STANDALONE, nb_of_workers=1)
        JobConfigChecker(config, collector).check()
        assert len(collector.errors) == 0

        tp.configure_job_executions(mode=JobConfig.MODE_VALUE_STANDALONE, nb_of_workers=2)
        JobConfigChecker(config, collector).check()
        assert len(collector.errors) == 1
