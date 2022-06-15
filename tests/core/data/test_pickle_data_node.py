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

import os
import pathlib

import pytest
from taipy.core.common.scope import Scope
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.pickle import PickleDataNode

from taipy.core.config.config import Config
from taipy.core.exceptions.exceptions import InvalidConfigurationId, NoData


class TestPickleDataNodeEntity:
    @pytest.fixture(scope="function", autouse=True)
    def remove_pickle_files(self):
        yield
        import glob

        for f in glob.glob("*.p"):
            print(f"deleting file {f}")
            os.remove(f)

    def test_create(self):
        dn = PickleDataNode("foobar_bazxyxea", Scope.PIPELINE, properties={"default_data": "Data"})
        assert os.path.isfile(Config.global_config.storage_folder + "pickles/" + dn.id + ".p")
        assert isinstance(dn, PickleDataNode)
        assert dn.storage_type() == "pickle"
        assert dn.config_id == "foobar_bazxyxea"
        assert dn.scope == Scope.PIPELINE
        assert dn.id is not None
        assert dn.name == dn.id
        assert dn.parent_id is None
        assert dn.last_edition_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.read() == "Data"
        assert dn.last_edition_date is not None
        assert dn.job_ids == []

        with pytest.raises(InvalidConfigurationId):
            PickleDataNode("foobar bazxyxea", Scope.PIPELINE, properties={"default_data": "Data"})

    def test_new_pickle_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node("not_ready_data_node_config_id", "pickle", path="NOT_EXISTING.p")
        not_ready_dn = _DataManager._get_or_create(not_ready_dn_cfg)
        assert not not_ready_dn.is_ready_for_reading

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.p")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "pickle", path=path)
        ready_dn = _DataManager._get_or_create(ready_dn_cfg)
        assert ready_dn.is_ready_for_reading

    def test_create_with_file_name(self):
        dn = PickleDataNode("foo", Scope.PIPELINE, properties={"default_data": "bar", "path": "foo.FILE.p"})
        assert os.path.isfile("foo.FILE.p")
        assert dn.read() == "bar"
        dn.write("qux")
        assert dn.read() == "qux"
        dn.write(1998)
        assert dn.read() == 1998

    def test_read_and_write(self):
        no_data_dn = PickleDataNode("foo", Scope.PIPELINE)
        with pytest.raises(NoData):
            assert no_data_dn.read() is None
            no_data_dn.read_or_raise()
        pickle_str = PickleDataNode("foo", Scope.PIPELINE, properties={"default_data": "bar"})
        assert isinstance(pickle_str.read(), str)
        assert pickle_str.read() == "bar"
        pickle_str.properties["default_data"] = "baz"  # this modifies the default data value but not the data itself
        assert pickle_str.read() == "bar"
        pickle_str.write("qux")
        assert pickle_str.read() == "qux"
        pickle_str.write(1998)
        assert pickle_str.read() == 1998
        assert isinstance(pickle_str.read(), int)
        pickle_int = PickleDataNode("foo", Scope.PIPELINE, properties={"default_data": 197})
        assert isinstance(pickle_int.read(), int)
        assert pickle_int.read() == 197
        pickle_dict = PickleDataNode(
            "foo", Scope.PIPELINE, properties={"default_data": {"bar": 12, "baz": "qux", "quux": [13]}}
        )
        assert isinstance(pickle_dict.read(), dict)
        assert pickle_dict.read() == {"bar": 12, "baz": "qux", "quux": [13]}

    def test_default_path_overrides_path(self):
        dn = PickleDataNode(
            "foo",
            Scope.PIPELINE,
            properties={
                "default_data": "bar",
                "default_path": "foo.FILE.p",
                "path": "bar.FILE.p",
            },
        )
        assert dn.path == "foo.FILE.p"

    def test_set_path(self):
        dn = PickleDataNode("foo", Scope.PIPELINE, properties={"default_path": "foo.p"})
        assert dn.path == "foo.p"
        dn.path = "bar.p"
        assert dn.path == "bar.p"

    def test_is_file_generated(self):
        dn = PickleDataNode("foo", Scope.PIPELINE, properties={})
        assert dn.is_file_generated
        dn.path = "bar.p"
        assert not dn.is_file_generated

    def test_path_deprecated(self):
        with pytest.warns(DeprecationWarning):
            PickleDataNode("foo", Scope.PIPELINE, properties={"path": "foo.p"})
