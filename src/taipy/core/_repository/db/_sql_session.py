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

from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from taipy.config.config import Config

from ...exceptions import MissingRequiredProperty
from .._decoder import loads
from .._encoder import dumps


class _SQLSession:
    _engine = None
    _SessionLocal = None

    @classmethod
    def init_db(cls):
        if cls._SessionLocal:
            return cls._SessionLocal

        cls._engine = _build_engine()
        cls._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls._engine)

        from ....core._version._version_model import _VersionModel
        from ....core.cycle._cycle_model import _CycleModel
        from ....core.data._data_model import _DataNodeModel
        from ....core.job._job_model import _JobModel
        from ....core.scenario._scenario_model import _ScenarioModel
        from ....core.task._task_model import _TaskModel

        _CycleModel.__table__.create(bind=cls._engine, checkfirst=True)
        _DataNodeModel.__table__.create(bind=cls._engine, checkfirst=True)
        _JobModel.__table__.create(bind=cls._engine, checkfirst=True)
        _ScenarioModel.__table__.create(bind=cls._engine, checkfirst=True)
        _TaskModel.__table__.create(bind=cls._engine, checkfirst=True)
        _VersionModel.__table__.create(bind=cls._engine, checkfirst=True)

        return cls._SessionLocal


@lru_cache
def _build_engine() -> Engine:
    properties = Config.core.repository_properties
    try:
        db_location = properties["db_location"]
    except KeyError:
        raise MissingRequiredProperty("Missing property db_location")

    # More sql databases can be easily added in the future
    engine = create_engine(
        f"sqlite:///{db_location}?check_same_thread=False",
        poolclass=StaticPool,
        json_serializer=dumps,
        json_deserializer=loads,
    )
    return engine
