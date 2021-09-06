from taipy.data.data_manager import DataManager
from taipy.data.data_source import EmbeddedDataSource


class TestDataManager:
    def test_create_and_fetch(self):
        dm = DataManager()
        dm.create_data_source(
            "ds_id",
            "test_data_source",
            "EmbeddedDataSource",
            {"data": "Embedded Data Source"},
        )

        ds = dm.fetch_data_source("ds_id")

        assert isinstance(ds, EmbeddedDataSource)

    def test_fetch_data_source_not_exists(self):
        dm = DataManager()
        ds = dm.fetch_data_source("test_data_source_2")

        assert ds is None
