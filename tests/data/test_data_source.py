from taipy.data import DataSourceConfig, Scope


class TestDataSource:
    def test_create_data_source(self):
        csv_ds = DataSourceConfig(name="Foo bar", type="csv", path="baz", has_header=True)
        assert csv_ds.name == "foo_bar"
        assert csv_ds.scope == Scope.PIPELINE
