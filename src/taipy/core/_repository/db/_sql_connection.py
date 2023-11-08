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

import sqlite3
from functools import lru_cache
from sqlite3 import Connection

from sqlalchemy.dialects import sqlite
from sqlalchemy.schema import CreateTable

from taipy.config.config import Config

from ...exceptions import MissingRequiredProperty


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class _SQLConnection:
    _connection = None

    @classmethod
    def init_db(cls):
        if cls._connection:
            return cls._connection

        cls._connection = _build_connection()
        cls._connection.row_factory = dict_factory

        from ..._version._version_model import _VersionModel
        from ...cycle._cycle_model import _CycleModel
        from ...data._data_model import _DataNodeModel
        from ...job._job_model import _JobModel
        from ...scenario._scenario_model import _ScenarioModel
        from ...task._task_model import _TaskModel
        from ...submission._submission_model import _SubmissionModel

        cls._connection.execute(
            str(CreateTable(_CycleModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        cls._connection.execute(
            str(CreateTable(_DataNodeModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        cls._connection.execute(
            str(CreateTable(_JobModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        cls._connection.execute(
            str(CreateTable(_ScenarioModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        cls._connection.execute(
            str(CreateTable(_TaskModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        cls._connection.execute(
            str(CreateTable(_VersionModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )
        cls._connection.execute(
            str(CreateTable(_SubmissionModel.__table__, if_not_exists=True).compile(dialect=sqlite.dialect()))
        )

        return cls._connection


def _build_connection() -> Connection:
    # Set SQLite threading mode to Serialized, means that threads may share the module, connections and cursors
    sqlite3.threadsafety = 3

    properties = Config.core.repository_properties
    try:
        db_location = properties["db_location"]
    except KeyError:
        raise MissingRequiredProperty("Missing property db_location")

    return __build_connection(db_location)


@lru_cache
def __build_connection(db_location: str):
    return sqlite3.connect(db_location, check_same_thread=False)
