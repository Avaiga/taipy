import datetime

from taipy.core.common.alias import DataNodeId, JobId
from taipy.core.common.scope import Scope
from taipy.core.data._data_manager import _DataManager
from taipy.core.data._data_model import _DataNodeModel
from taipy.core.data.csv import CSVDataNode
from taipy.core.data.data_node import DataNode

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("dn_id"),
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [JobId("job_id")],
    None,
    False,
    {"path": "/path", "has_header": True},
)

data_node_model = _DataNodeModel(
    "dn_id",
    "test_data_node",
    Scope.PIPELINE,
    "csv",
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0).isoformat(),
    [JobId("job_id")],
    None,
    None,
    False,
    {"path": "/path", "has_header": True},
)


class TestDataRepository:
    def test_save_and_load(self, tmpdir):
        repository = _DataManager._repository
        repository.base_path = tmpdir
        repository._save(data_node)
        dn = repository.load("dn_id")

        assert isinstance(dn, CSVDataNode)
        assert isinstance(dn, DataNode)

    def test_from_and_to_model(self):
        repository = _DataManager._repository
        assert repository._to_model(data_node) == data_node_model
        assert repository._from_model(data_node_model) == data_node
