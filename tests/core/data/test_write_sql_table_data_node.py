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

from importlib import util
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from taipy.config.common.scope import Scope
from taipy.core.data.sql_table import SQLTableDataNode


class MyCustomObject:
    def __init__(self, x=None, y=None):
        self.x = x
        self.y = y


class TestWriteSQLTableDataNode:
    __sql_properties = [
        {
            "db_name": "taipy",
            "db_engine": "sqlite",
            "table_name": "example",
            "db_extra_args": {
                "TrustServerCertificate": "yes",
                "other": "value",
            },
        },
    ]

    if util.find_spec("pyodbc"):
        __sql_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mssql",
                "table_name": "example",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    if util.find_spec("pymysql"):
        __sql_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "mysql",
                "table_name": "example",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    if util.find_spec("psycopg2"):
        __sql_properties.append(
            {
                "db_username": "sa",
                "db_password": "Passw0rd",
                "db_name": "taipy",
                "db_engine": "postgresql",
                "table_name": "example",
                "db_extra_args": {
                    "TrustServerCertificate": "yes",
                },
            },
        )

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_write_pandas(self, properties):
        custom_properties = properties.copy()
        custom_properties.pop("db_extra_args")
        sql_table_dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ) as _:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            with patch("taipy.core.data.sql_table.SQLTableDataNode._insert_dataframe") as mck:
                df = pd.DataFrame([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}])
                sql_table_dn.write(df)
                assert mck.call_count == 1

                sql_table_dn.write(df["a"])
                assert mck.call_count == 2

                sql_table_dn.write(pd.DataFrame())
                assert mck.call_count == 3

                series = pd.Series([1, 2, 3])
                sql_table_dn.write(series)
                assert mck.call_count == 4

                sql_table_dn.write(None)
                assert mck.call_count == 5

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_write_numpy(self, properties):
        custom_properties = properties.copy()
        custom_properties["exposed_type"] = "numpy"
        custom_properties.pop("db_extra_args")
        sql_table_dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ) as _:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            with patch("taipy.core.data.sql_table.SQLTableDataNode._insert_dataframe") as mck:
                arr = np.array([[1], [2], [3], [4], [5]])
                sql_table_dn.write(arr)
                assert mck.call_count == 1

                sql_table_dn.write(arr[0:3])
                assert mck.call_count == 2

                sql_table_dn.write(np.array([]))
                assert mck.call_count == 3

                sql_table_dn.write(None)
                assert mck.call_count == 4

    @pytest.mark.parametrize("properties", __sql_properties)
    def test_write_custom_exposed_type(self, properties):
        custom_properties = properties.copy()
        custom_properties["exposed_type"] = MyCustomObject
        custom_properties.pop("db_extra_args")
        sql_table_dn = SQLTableDataNode("foo", Scope.SCENARIO, properties=custom_properties)

        with patch("sqlalchemy.engine.Engine.connect") as engine_mock, patch(
            "taipy.core.data.sql_table.SQLTableDataNode._create_table"
        ) as _:
            cursor_mock = engine_mock.return_value.__enter__.return_value
            cursor_mock.execute.side_effect = None

            with patch("taipy.core.data.sql_table.SQLTableDataNode._insert_dataframe") as mck:
                custom_data = [
                    MyCustomObject(1, 2),
                    MyCustomObject(3, 4),
                    MyCustomObject(None, 2),
                    MyCustomObject(1, None),
                    MyCustomObject(None, None),
                ]
                sql_table_dn.write(custom_data)
                assert mck.call_count == 1

                sql_table_dn.write(None)
                assert mck.call_count == 2

    def test_sqlite_append_pandas(self, tmp_sqlite_sqlite3_file_path):
        folder_path, db_name, file_extension = tmp_sqlite_sqlite3_file_path
        properties = {
            "db_engine": "sqlite",
            "table_name": "example",
            "db_name": db_name,
            "sqlite_folder_path": folder_path,
            "sqlite_file_extension": file_extension,
        }

        dn = SQLTableDataNode("sqlite_dn", Scope.SCENARIO, properties=properties)
        original_data = pd.DataFrame([{"foo": 1, "bar": 2}, {"foo": 3, "bar": 4}])
        data = dn.read()
        assert_frame_equal(data, original_data)

        append_data_1 = pd.DataFrame([{"foo": 5, "bar": 6}, {"foo": 7, "bar": 8}])
        dn.append(append_data_1)
        assert_frame_equal(dn.read(), pd.concat([original_data, append_data_1]).reset_index(drop=True))
