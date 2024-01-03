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

import os
import pathlib
from datetime import datetime
from time import sleep

import modin.pandas as modin_pd
import pandas as pd
import pytest

from taipy.config.common.scope import Scope
from taipy.config.config import Config
from taipy.config.exceptions.exceptions import InvalidConfigurationId
from taipy.core.data._data_manager import _DataManager
from taipy.core.data.pickle import PickleDataNode
from taipy.core.exceptions.exceptions import NoData


@pytest.fixture(scope="function", autouse=True)
def cleanup():
    yield
    path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.p")
    if os.path.isfile(path):
        os.remove(path)


class TestPickleDataNodeEntity:
    @pytest.fixture(scope="function", autouse=True)
    def remove_pickle_files(self):
        yield
        import glob

        for f in glob.glob("*.p"):
            os.remove(f)

    def test_create(self):
        dn = PickleDataNode("foobar_bazxyxea", Scope.SCENARIO, properties={"default_data": "Data"})
        assert os.path.isfile(Config.core.storage_folder + "pickles/" + dn.id + ".p")
        assert isinstance(dn, PickleDataNode)
        assert dn.storage_type() == "pickle"
        assert dn.config_id == "foobar_bazxyxea"
        assert dn.scope == Scope.SCENARIO
        assert dn.id is not None
        assert dn.name is None
        assert dn.owner_id is None
        assert dn.last_edit_date is not None
        assert dn.job_ids == []
        assert dn.is_ready_for_reading
        assert dn.read() == "Data"
        assert dn.last_edit_date is not None
        assert dn.job_ids == []

        with pytest.raises(InvalidConfigurationId):
            PickleDataNode("foobar bazxyxea", Scope.SCENARIO, properties={"default_data": "Data"})

    def test_get_user_properties(self, pickle_file_path):
        dn_1 = PickleDataNode("dn_1", Scope.SCENARIO, properties={"path": pickle_file_path})
        assert dn_1._get_user_properties() == {}

        dn_2 = PickleDataNode(
            "dn_2",
            Scope.SCENARIO,
            properties={
                "default_data": "foo",
                "default_path": pickle_file_path,
                "foo": "bar",
            },
        )

        # default_data, default_path, path, is_generated are filtered out
        assert dn_2._get_user_properties() == {"foo": "bar"}

    def test_new_pickle_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.configure_data_node("not_ready_data_node_config_id", "pickle", path="NOT_EXISTING.p")
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.p")
        ready_dn_cfg = Config.configure_data_node("ready_data_node_config_id", "pickle", path=path)

        dns = _DataManager._bulk_get_or_create([not_ready_dn_cfg, ready_dn_cfg])

        assert not dns[not_ready_dn_cfg].is_ready_for_reading
        assert dns[ready_dn_cfg].is_ready_for_reading

    def test_create_with_file_name(self):
        dn = PickleDataNode("foo", Scope.SCENARIO, properties={"default_data": "bar", "path": "foo.FILE.p"})
        assert os.path.isfile("foo.FILE.p")
        assert dn.read() == "bar"
        dn.write("qux")
        assert dn.read() == "qux"
        dn.write(1998)
        assert dn.read() == 1998

    def test_read_and_write(self):
        no_data_dn = PickleDataNode("foo", Scope.SCENARIO)
        with pytest.raises(NoData):
            assert no_data_dn.read() is None
            no_data_dn.read_or_raise()
        pickle_str = PickleDataNode("foo", Scope.SCENARIO, properties={"default_data": "bar"})
        assert isinstance(pickle_str.read(), str)
        assert pickle_str.read() == "bar"
        pickle_str.properties["default_data"] = "baz"  # this modifies the default data value but not the data itself
        assert pickle_str.read() == "bar"
        pickle_str.write("qux")
        assert pickle_str.read() == "qux"
        pickle_str.write(1998)
        assert pickle_str.read() == 1998
        assert isinstance(pickle_str.read(), int)
        pickle_int = PickleDataNode("foo", Scope.SCENARIO, properties={"default_data": 197})
        assert isinstance(pickle_int.read(), int)
        assert pickle_int.read() == 197
        pickle_dict = PickleDataNode(
            "foo", Scope.SCENARIO, properties={"default_data": {"bar": 12, "baz": "qux", "quux": [13]}}
        )
        assert isinstance(pickle_dict.read(), dict)
        assert pickle_dict.read() == {"bar": 12, "baz": "qux", "quux": [13]}

    @pytest.mark.modin
    def test_read_and_write_modin(self):
        default_pandas = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        new_pandas_df = pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]})
        default_modin = modin_pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        new_modin_df = modin_pd.DataFrame({"c": [7, 8, 9], "d": [10, 11, 12]})

        pickle_pandas = PickleDataNode("foo", Scope.SCENARIO, properties={"default_data": default_pandas})
        assert isinstance(pickle_pandas.read(), pd.DataFrame)
        assert default_pandas.equals(pickle_pandas.read())
        pickle_pandas.write(new_pandas_df)
        assert new_pandas_df.equals(pickle_pandas.read())
        assert isinstance(pickle_pandas.read(), pd.DataFrame)
        pickle_pandas.write(new_modin_df)
        assert new_modin_df.equals(pickle_pandas.read())
        assert isinstance(pickle_pandas.read(), modin_pd.DataFrame)
        pickle_pandas.write(1998)
        assert pickle_pandas.read() == 1998
        assert isinstance(pickle_pandas.read(), int)

        pickle_modin = PickleDataNode("foo", Scope.SCENARIO, properties={"default_data": default_modin})
        assert isinstance(pickle_modin.read(), modin_pd.DataFrame)
        assert default_modin.equals(pickle_modin.read())
        pickle_modin.write(new_modin_df)
        assert new_modin_df.equals(pickle_modin.read())
        assert isinstance(pickle_modin.read(), modin_pd.DataFrame)
        pickle_modin.write(new_pandas_df)
        assert new_pandas_df.equals(pickle_modin.read())
        assert isinstance(pickle_modin.read(), pd.DataFrame)
        pickle_modin.write(1998)
        assert pickle_modin.read() == 1998
        assert isinstance(pickle_modin.read(), int)

    def test_path_overrides_default_path(self):
        dn = PickleDataNode(
            "foo",
            Scope.SCENARIO,
            properties={
                "default_data": "bar",
                "default_path": "foo.FILE.p",
                "path": "bar.FILE.p",
            },
        )
        assert dn.path == "bar.FILE.p"

    def test_set_path(self):
        dn = PickleDataNode("foo", Scope.SCENARIO, properties={"default_path": "foo.p"})
        assert dn.path == "foo.p"
        dn.path = "bar.p"
        assert dn.path == "bar.p"

    def test_is_generated(self):
        dn = PickleDataNode("foo", Scope.SCENARIO, properties={})
        assert dn.is_generated
        dn.path = "bar.p"
        assert not dn.is_generated

    def test_read_write_after_modify_path(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.p")
        new_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/temp.p")
        dn = PickleDataNode("foo", Scope.SCENARIO, properties={"default_path": path})
        read_data = dn.read()
        assert read_data is not None
        dn.path = new_path
        with pytest.raises(FileNotFoundError):
            dn.read()
        dn.write({"other": "stuff"})
        assert dn.read() == {"other": "stuff"}

    def test_get_system_modified_date_instead_of_last_edit_date(self, tmpdir_factory):
        temp_file_path = str(tmpdir_factory.mktemp("data").join("temp.pickle"))
        pd.DataFrame([]).to_pickle(temp_file_path)
        dn = PickleDataNode("foo", Scope.SCENARIO, properties={"path": temp_file_path, "exposed_type": "pandas"})

        dn.write(pd.DataFrame([1, 2, 3]))
        previous_edit_date = dn.last_edit_date

        sleep(0.1)

        pd.DataFrame([4, 5, 6]).to_pickle(temp_file_path)
        new_edit_date = datetime.fromtimestamp(os.path.getmtime(temp_file_path))

        assert previous_edit_date < dn.last_edit_date
        assert new_edit_date == dn.last_edit_date

        sleep(0.1)

        dn.write(pd.DataFrame([7, 8, 9]))
        assert new_edit_date < dn.last_edit_date
        os.unlink(temp_file_path)
