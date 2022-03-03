from typing import Dict

from taipy.core.config._config import _Config
from taipy.core.config.checker.checkers.config_checker import ConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.data_node_config import DataNodeConfig
from taipy.core.config.job_config import JobConfig


class JobConfigChecker(ConfigChecker):
    def __init__(self, config: _Config, collector: IssueCollector):
        super().__init__(config, collector)

    def check(self) -> IssueCollector:
        job_config = self.config.job_config
        data_node_configs = self.config.data_nodes
        self._check_multiprocess_mode(job_config, data_node_configs)
        return self.collector

    def _check_multiprocess_mode(self, job_config: JobConfig, data_node_configs: Dict[str, DataNodeConfig]):
        if job_config.is_multiprocess:
            for cfg_id, data_node_config in data_node_configs.items():
                if data_node_config.storage_type == DataNodeConfig.STORAGE_TYPE_VALUE_IN_MEMORY:
                    self._error(
                        DataNodeConfig.STORAGE_TYPE_KEY,
                        data_node_config.storage_type,
                        f"DataNode {cfg_id}: In-memory storage type cannot be used in multiprocess mode",
                    )
