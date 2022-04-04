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

from taipy.core.config.checker._checkers._data_node_config_checker import _DataNodeConfigChecker
from taipy.core.config.checker._checkers._gLobal_config_checker import _GlobalConfigChecker
from taipy.core.config.checker._checkers._job_config_checker import _JobConfigChecker
from taipy.core.config.checker._checkers._pipeline_config_checker import _PipelineConfigChecker
from taipy.core.config.checker._checkers._scenario_config_checker import _ScenarioConfigChecker
from taipy.core.config.checker._checkers._task_config_checker import _TaskConfigChecker
from taipy.core.config.checker.issue_collector import IssueCollector


class _Checker:
    """holds the various checkers to perform on the config."""

    _default_checkers = {
        _GlobalConfigChecker,
        _DataNodeConfigChecker,
        _TaskConfigChecker,
        _PipelineConfigChecker,
        _ScenarioConfigChecker,
        _JobConfigChecker,
    }

    def __init__(self):
        self._checkers = list(self._default_checkers)

    def _check(self, _applied_config):
        collector = IssueCollector()
        for checker in self._checkers:
            checker(_applied_config, collector)._check()
        return collector
