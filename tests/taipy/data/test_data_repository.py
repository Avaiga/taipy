import datetime

from taipy.common.alias import DataNodeId, JobId
from taipy.data import CSVDataNode, DataNode, Scope
from taipy.data.data_node_model import DataNodeModel
from taipy.data.manager import DataManager

data_node = CSVDataNode(
    "test_data_node",
    Scope.PIPELINE,
    DataNodeId("ds_id"),
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0),
    [JobId("job_id")],
    None,
    None,
    None,
    False,
    {"path": "/path", "has_header": True},
)

data_node_model = DataNodeModel(
    "ds_id",
    "test_data_node",
    Scope.PIPELINE,
    "csv",
    "name",
    "parent_id",
    datetime.datetime(1985, 10, 14, 2, 30, 0).isoformat(),
    [JobId("job_id")],
    None,
    None,
    None,
    False,
    {"path": "/path", "has_header": True},
)


class TestDataRepository:
    def test_save_and_load(self, tmpdir):
        repository = DataManager().repository
        repository.base_path = tmpdir
        repository.save(data_node)
        ds = repository.load("ds_id")

        assert isinstance(ds, CSVDataNode)
        assert isinstance(ds, DataNode)

    def test_from_and_to_model(self):
        repository = DataManager().repository
        assert repository.to_model(data_node) == data_node_model
        assert repository.from_model(data_node_model) == data_node
