from taipy.config import DataSourceConfig
from taipy.data import Scope


class TestDataSource:
    def test_create_data_source(self):
        csv_ds = DataSourceConfig(name="Foo/bar ξ", type="csv", path="baz", has_header=True)
        assert csv_ds.type == "csv"
        assert csv_ds.name == "foo-bar_x"
        assert csv_ds.scope == Scope.PIPELINE
        assert csv_ds.properties["path"] == "baz"
        