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

from unittest import mock

from taipy.core import Config, Scope


class TestConfig:
    def test_configure_csv_data_node(self):
        a, b, c, d, e = "foo", "path", True, Scope.PIPELINE, "numpy"
        with mock.patch("taipy.core.config.config.Config.configure_data_node") as mck:
            Config.configure_csv_data_node(a, b, c, d, exposed_type=e)
            mck.assert_called_once_with(a, "csv", scope=d, default_path=b, has_header=c, exposed_type=e)

    def test_configure_excel_data_node(self):
        a, b, c, d, e, f = "foo", "path", True, "Sheet1", Scope.PIPELINE, "numpy"
        with mock.patch("taipy.core.config.config.Config.configure_data_node") as mck:
            Config.configure_excel_data_node(a, b, c, d, e, exposed_type=f)
            mck.assert_called_once_with(a, "excel", scope=e, default_path=b, has_header=c, sheet_name=d, exposed_type=f)

    def test_configure_generic_data_node(self):
        a, b, c, d, e, f, g = "foo", print, print, Scope.PIPELINE, tuple([]), tuple([]), "qux"
        with mock.patch("taipy.core.config.config.Config.configure_data_node") as mck:
            Config.configure_generic_data_node(a, b, c, e, f, d, property=g)
            mck.assert_called_once_with(
                a, "generic", scope=d, read_fct=b, write_fct=c, read_fct_params=e, write_fct_params=f, property=g
            )

    def test_configure_in_memory_data_node(self):
        a, b, c, d = "foo", 0, Scope.PIPELINE, "qux"
        with mock.patch("taipy.core.config.config.Config.configure_data_node") as mck:
            Config.configure_in_memory_data_node(a, b, c, property=d)
            mck.assert_called_once_with(a, "in_memory", scope=c, default_data=b, property=d)

    def test_configure_pickle_data_node(self):
        a, b, c, d = "foo", 0, Scope.PIPELINE, "path"
        with mock.patch("taipy.core.config.config.Config.configure_data_node") as mck:
            Config.configure_pickle_data_node(a, b, c, path=d)
            mck.assert_called_once_with(a, "pickle", scope=c, default_data=b, path=d)

    def test_configure_sql_data_node(self):
        a, b, c, d, e, f, g, h, i, j, scope, k = (
            "foo",
            "user",
            "pwd",
            "db",
            "engine",
            "read",
            "write",
            "port",
            "host",
            "driver",
            Scope.PIPELINE,
            "qux",
        )
        with mock.patch("taipy.core.config.config.Config.configure_data_node") as mck:
            Config.configure_sql_data_node(a, b, c, d, e, f, g, h, i, j, scope=scope, property=k)
            mck.assert_called_once_with(
                a,
                "sql",
                scope=scope,
                db_username=b,
                db_password=c,
                db_name=d,
                db_engine=e,
                read_query=f,
                write_table=g,
                db_port=h,
                db_host=i,
                db_driver=j,
                property=k,
            )
