import os
import pathlib

import pytest

from taipy.config import Config
from taipy.data import PickleDataNode
from taipy.data.manager import DataManager
from taipy.data.scope import Scope
from taipy.exceptions.data_node import NoData


class TestPickleDataNodeEntity:
    @pytest.fixture(scope="function", autouse=True)
    def remove_pickle_files(self):
        yield
        import glob

        for f in glob.glob("*.p"):
            print(f"deleting file {f}")
            os.remove(f)

    def test_create(self):
        ds = PickleDataNode("foobar BaZξyₓéà", Scope.PIPELINE, properties={"default_data": "Data"})
        assert os.path.isfile(Config.global_config().storage_folder + "pickles/" + ds.id + ".p")
        assert isinstance(ds, PickleDataNode)
        assert ds.storage_type() == "pickle"
        assert ds.config_name == "foobar_bazxyxea"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.name == ds.id
        assert ds.parent_id is None
        assert ds.last_edition_date is not None
        assert ds.job_ids == []
        assert ds.is_ready_for_reading
        assert ds.read() == "Data"
        assert ds.default_data == "Data"
        assert ds.last_edition_date is not None
        assert ds.job_ids == []

    def test_new_pickle_data_node_with_existing_file_is_ready_for_reading(self):
        not_ready_dn_cfg = Config.add_data_node("not_ready_data_node_config_name", "pickle", file_path="NOT_EXISTING.p")
        not_ready_dn = DataManager().get_or_create(not_ready_dn_cfg)
        assert not not_ready_dn.is_ready_for_reading

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.p")
        ready_dn_cfg = Config.add_data_node("ready_data_node_config_name", "pickle", file_path=path)
        ready_dn = DataManager().get_or_create(ready_dn_cfg)
        assert ready_dn.is_ready_for_reading

    def test_create_with_file_name(self):
        ds = PickleDataNode("foo", Scope.PIPELINE, properties={"default_data": "bar", "file_path": "foo.FILE.p"})
        assert os.path.isfile("foo.FILE.p")
        assert ds.read() == "bar"
        ds.write("qux")
        assert ds.read() == "qux"
        ds.write(1998)
        assert ds.read() == 1998

    def test_read_and_write(self):
        no_data_ds = PickleDataNode("foo", Scope.PIPELINE)
        with pytest.raises(NoData):
            no_data_ds.read()
        pickle_str = PickleDataNode("foo", Scope.PIPELINE, properties={"default_data": "bar"})
        assert isinstance(pickle_str.read(), str)
        assert pickle_str.read() == "bar"
        assert pickle_str.default_data == "bar"
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
