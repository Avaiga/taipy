import datetime

from taipy.common.alias import DataSourceId, JobId
from taipy.data import CSVDataSource, DataSource, Scope
from taipy.data.data_source_model import DataSourceModel
from taipy.data.manager import DataManager

data_source = CSVDataSource(
    "test_data_source",
    Scope.PIPELINE,
    DataSourceId("ds_id"),
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

data_source_model = DataSourceModel(
    "ds_id",
    "test_data_source",
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
        repository.save(data_source)
        ds = repository.load("ds_id")

        assert isinstance(ds, CSVDataSource)
        assert isinstance(ds, DataSource)

    def test_from_and_to_model(self):
        repository = DataManager().repository
        assert repository.to_model(data_source) == data_source_model
        assert repository.from_model(data_source_model) == data_source
