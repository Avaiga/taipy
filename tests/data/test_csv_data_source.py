import datetime
import os
import pathlib

import numpy as np
import pandas as pd
import pytest

from taipy.data import CSVDataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty
from taipy.exceptions.data_source import NoData


class TestCSVDataSourceEntity:
    def test_get(self):
        not_existing_csv = CSVDataSource.create("foo", Scope.PIPELINE, None, "NOT_EXISTING_PATH.csv")
        with pytest.raises(NoData):
            not_existing_csv.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        csv = CSVDataSource.create("bar", Scope.PIPELINE, None, path)
        assert csv.path == path
        csv.last_edition_date = datetime.datetime.now()
        data = csv.read()
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
        csv = CSVDataSource.create("foo", Scope.PIPELINE, None, csv_file)
        assert np.array_equal(csv.read().values, default_data_frame.values)

        if not columns:
            csv.write(content)
            df = pd.DataFrame(content)
        else:
            csv.write_with_column_names(content, columns)
            df = pd.DataFrame(content, columns=columns)

        assert np.array_equal(csv.read().values, df.values)

    def test_create(self):
        ds = CSVDataSource.create("fOo BAr", Scope.PIPELINE, None, "data/source/path")

        assert isinstance(ds, CSVDataSource)
        assert ds.config_name == "foo_bar"
        assert ds.has_header is False
        assert ds.path == "data/source/path"
        assert ds.type() == "csv"
        assert ds.id is not None
        assert ds.last_edition_date is None
        assert ds.job_ids == []
        with pytest.raises(AttributeError):
            ds.foo

    def test_init_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            CSVDataSource("foo", Scope.PIPELINE, "ds_id", {})

    def test_preview(self):
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.csv")
        ds = CSVDataSource.create("foo", Scope.PIPELINE, None, path)
        ds.preview()
