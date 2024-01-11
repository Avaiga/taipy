# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


class NotifyMock:
    """
    A shared class for testing notification on jobStatus of sequence level and scenario level

    "entity" can be understood as either "scenario" or "sequence".
    """

    def __init__(self, entity):
        self.scenario = entity
        self.nb_called = 0
        self.__name__ = "NotifyMock"

    def __call__(self, entity, job):
        assert entity == self.scenario
        if self.nb_called == 0:
            assert job.is_pending()
        if self.nb_called == 1:
            assert job.is_running()
        if self.nb_called == 2:
            assert job.is_finished()
        self.nb_called += 1

    def assert_called_3_times(self):
        assert self.nb_called == 3

    def assert_not_called(self):
        assert self.nb_called == 0

    def reset(self):
        self.nb_called = 0
