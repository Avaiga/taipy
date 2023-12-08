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

from datetime import timedelta

from taipy.config import Config
from taipy.config.common.scope import Scope


class TestConfig:
    def test_configure_csv_data_node(self):
        a, b, c, d, e, f = "foo", "path", True, "numpy", Scope.SCENARIO, timedelta(1)
        Config.configure_csv_data_node(a, b, c, d, e, f)
        assert len(Config.data_nodes) == 2

    def test_configure_excel_data_node(self):
        a, b, c, d, e, f, g = "foo", "path", True, "Sheet1", "numpy", Scope.SCENARIO, timedelta(1)
        Config.configure_excel_data_node(a, b, c, d, e, f, g)
        assert len(Config.data_nodes) == 2

    def test_configure_generic_data_node(self):
        a, b, c, d, e, f, g, h = "foo", print, print, tuple([]), tuple([]), Scope.SCENARIO, timedelta(1), "qux"
        Config.configure_generic_data_node(a, b, c, d, e, f, g, property=h)
        assert len(Config.data_nodes) == 2

    def test_configure_in_memory_data_node(self):
        a, b, c, d, e = "foo", 0, Scope.SCENARIO, timedelta(1), "qux"
        Config.configure_in_memory_data_node(a, b, c, d, property=e)
        assert len(Config.data_nodes) == 2

    def test_configure_pickle_data_node(self):
        a, b, c, d, e = "foo", 0, Scope.SCENARIO, timedelta(1), "path"
        Config.configure_pickle_data_node(a, b, c, d, path=e)
        assert len(Config.data_nodes) == 2

    def test_configure_json_data_node(self):
        a, dp, ec, dc, sc, f, p = "foo", "path", "ec", "dc", Scope.SCENARIO, timedelta(1), "qux"
        Config.configure_json_data_node(a, dp, ec, dc, sc, f, path=p)
        assert len(Config.data_nodes) == 2

    def test_configure_sql_table_data_node(self):
        a, b, c, d, e, f, g, h, i, extra_args, exposed_type, scope, vp, k = (
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
            timedelta(1),
            "qux",
        )
        Config.configure_sql_table_data_node(a, b, c, d, e, f, g, h, i, extra_args, exposed_type, scope, vp, property=k)
        assert len(Config.data_nodes) == 2

    def test_configure_sql_data_node(self):
        a, b, c, d, e, f, g, h, i, j, k, extra_args, exposed_type, scope, vp, k = (
            "foo",
            "user",
            "pwd",
            "db",
            "engine",
            "read_query",
            "write_query_builder",
            "append_query_builder",
            "port",
            "host",
            "driver",
            {"foo": "bar"},
            "exposed_type",
            Scope.SCENARIO,
            timedelta(1),
            "qux",
        )
        Config.configure_sql_data_node(a, b, c, d, e, f, g, h, i, j, k, extra_args, exposed_type, scope, vp, property=k)
        assert len(Config.data_nodes) == 2

    def test_configure_mongo_data_node(self):
        a, b, c, d, e, f, g, h, extra_args, scope, vp, k = (
            "foo",
            "db_name",
            "collection_name",
            None,
            "user",
            "pwd",
            "host",
            "port",
            {"foo": "bar"},
            Scope.SCENARIO,
            timedelta(1),
            "qux",
        )
        Config.configure_mongo_collection_data_node(a, b, c, d, e, f, g, h, extra_args, scope, vp, property=k)
        assert len(Config.data_nodes) == 2

    def test_configure_s3_object_data_node(self):
        a, b, c, d, e, f, extra_args, scope, vp, k = (
            "foo",
            "access_key",
            "secret_acces_key",
            "s3_bucket_name",
            "s3_object_key",
            None,
            {"foo": "bar"},
            Scope.SCENARIO,
            timedelta(1),
            "qux",
        )
        Config.configure_s3_object_data_node(a, b, c, d, e, f, extra_args, scope, vp, property=k)
        assert len(Config.data_nodes) == 2
        
