# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import taipy.core.taipy as tp
from taipy.core.config.checker._checkers._job_config_checker import _JobConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector
from taipy.core.config.config import Config
from taipy.core.config.job_config import JobConfig
from taipy.core.data._data_manager import _DataManager


class TestJobConfigChecker:
    def test_check_multiprocess_mode(self):
        collector = IssueCollector()
        config = Config._python_config
        _JobConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0

        dn_config_1 = Config.configure_data_node(id="foo", storage_type="in_memory")
        _DataManager._get_or_create(dn_config_1)
        assert len(tp.get_data_nodes()) == 1

        Config.configure_job_executions(mode=JobConfig._DEFAULT_MODE, nb_of_workers=1)
        _JobConfigChecker(config, collector)._check()
        assert len(collector.errors) == 0

        Config.configure_job_executions(mode=JobConfig._DEFAULT_MODE, nb_of_workers=2)
        _JobConfigChecker(config, collector)._check()
        assert len(collector.errors) == 1
