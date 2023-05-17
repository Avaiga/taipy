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

from taipy.config import Config
from taipy.config.common.scope import Scope


class TestConfig:
    def test_configure_csv_data_node(self):
        a, b, c, d, e = "foo", "path", True, Scope.SCENARIO, "numpy"
        Config.configure_csv_data_node(a, b, c, d, e)
        assert len(Config.data_nodes) == 2

    def test_configure_excel_data_node(self):
        a, b, c, d, e, f = "foo", "path", True, "Sheet1", Scope.SCENARIO, "numpy"
        Config.configure_excel_data_node(a, b, c, d, e, f)
        assert len(Config.data_nodes) == 2

    def test_configure_generic_data_node(self):
        a, b, c, d, e, f, g = "foo", print, print, Scope.SCENARIO, tuple([]), tuple([]), "qux"
        Config.configure_generic_data_node(a, b, c, e, f, d, property=g)
        assert len(Config.data_nodes) == 2

    def test_configure_in_memory_data_node(self):
        a, b, c, d = "foo", 0, Scope.SCENARIO, "qux"
        Config.configure_in_memory_data_node(a, b, c, property=d)
        assert len(Config.data_nodes) == 2

    def test_configure_pickle_data_node(self):
        a, b, c, d = "foo", 0, Scope.SCENARIO, "path"
        Config.configure_pickle_data_node(a, b, c, path=d)
        assert len(Config.data_nodes) == 2

    def test_configure_json_data_node(self):
        a, dp, ec, dc, sc, p = "foo", "path", "ec", "dc", Scope.SCENARIO, "qux"
        Config.configure_json_data_node(a, dp, ec, dc, sc, path=p)
        assert len(Config.data_nodes) == 2

    def test_configure_sql_table_data_node(self):
        a, b, c, d, e, f, g, h, i, extra_args, exposed_type, scope, k = (
            "foo",
            "user",
            "pwd",
            "db",
            "engine",
            "table_name",
            "port",
            "host",
            "driver",
            {"foo": "bar"},
            "exposed_type",
            Scope.SCENARIO,
            "qux",
        )
        Config.configure_sql_table_data_node(
            a, b, c, d, e, f, g, h, i, extra_args, exposed_type, scope=scope, property=k
        )
        assert len(Config.data_nodes) == 2

    def test_configure_sql_data_node(self):
        a, b, c, d, e, f, g, h, i, j, extra_args, exposed_type, scope, k = (
            "foo",
            "user",
            "pwd",
            "db",
            "engine",
            "read_query",
            "write_query_builder",
            "port",
            "host",
            "driver",
            {"foo": "bar"},
            "exposed_type",
            Scope.SCENARIO,
            "qux",
        )
        Config.configure_sql_data_node(a, b, c, d, e, f, g, h, i, j, extra_args, exposed_type, scope=scope, property=k)
        assert len(Config.data_nodes) == 2
