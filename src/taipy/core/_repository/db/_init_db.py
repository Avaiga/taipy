# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from ._sql_session import engine


def run_once(fn):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return fn(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


@run_once
def init_db() -> None:
    from ....core._version._version_model import _VersionModel
    from ....core.cycle._cycle_model import _CycleModel
    from ....core.data._data_model import _DataNodeModel
    from ....core.job._job_model import _JobModel
    from ....core.scenario._scenario_model import _ScenarioModel
    from ....core.task._task_model import _TaskModel

    _CycleModel.__table__.create(bind=engine, checkfirst=True)
    _DataNodeModel.__table__.create(bind=engine, checkfirst=True)
    _JobModel.__table__.create(bind=engine, checkfirst=True)
    _ScenarioModel.__table__.create(bind=engine, checkfirst=True)
    _TaskModel.__table__.create(bind=engine, checkfirst=True)
    _VersionModel.__table__.create(bind=engine, checkfirst=True)
