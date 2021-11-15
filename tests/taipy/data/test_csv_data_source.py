import datetime
import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.common.alias import DataSourceId
from taipy.data import CSVDataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty
from taipy.exceptions.data_source import NoData


class TestCSVDataSource:
    def test_create(self):
        path = "data/source/path"
        ds = CSVDataSource("fOo BAr", Scope.PIPELINE, name="super name", properties={"path": path, "has_header": False})
        assert isinstance(ds, CSVDataSource)
        assert ds.type() == "csv"
        assert ds.config_name == "foo_bar"
        assert ds.name == "super name"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.parent_id is None
        assert ds.last_edition_date is None
        assert ds.job_ids == []
        assert not ds.up_to_date
        assert ds.path == path
        assert ds.has_header is False

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"))
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={})
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={"path": "path"})
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={"has_header": True})

    def test_read(self):
        not_existing_csv = CSVDataSource("foo", Scope.PIPELINE, properties={"path": "WRONG.csv", "has_header": False})
        with pytest.raises(NoData):
            not_existing_csv.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        csv_ds = CSVDataSource("bar", Scope.PIPELINE, properties={"path": path, "has_header": False})
        assert csv_ds.path == path
        csv_ds.last_edition_date = datetime.datetime.now()
        data = csv_ds.read()
        assert isinstance(data, pd.DataFrame)

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, csv_file, default_data_frame, content, columns):
        csv_ds = CSVDataSource("foo", Scope.PIPELINE, properties={"path": csv_file, "has_header": False})
        assert np.array_equal(csv_ds.read().values, default_data_frame.values)
        if not columns:
            csv_ds.write(content)
            df = pd.DataFrame(content)
        else:
            csv_ds.write_with_column_names(content, columns)
            df = pd.DataFrame(content, columns=columns)
        assert np.array_equal(csv_ds.read().values, df.values)

    def test_preview(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ds = CSVDataSource("foo", Scope.PIPELINE, properties={"path": path, "has_header": False})
        ds.preview()
