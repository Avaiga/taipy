from taipy.data import DataSource, Scope


class TestDataSource:
    def test_create_data_source(self):
        csv_ds = DataSource(name="Foo bar", type="csv", path="baz", has_header=True)
        assert csv_ds.name == "foo_bar"
        assert csv_ds.scope == Scope.PIPELINE
