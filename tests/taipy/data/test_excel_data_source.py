import datetime
import os
import pathlib
from unittest import mock

import numpy as np
import pandas as pd
import pytest

from taipy.common.alias import DataSourceId
from taipy.data.excel import ExcelDataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty
from taipy.exceptions.data_source import NoData


class TestCSVDataSource:
    def test_create(self):
        path = "data/source/path"
        sheet_names = ["sheet_name_1", "sheet_name_2"]
        ds = ExcelDataSource(
            "fOo BAr",
            Scope.PIPELINE,
            name="super name",
            properties={"path": path, "has_header": False, "sheet_name": sheet_names},
        )
        assert isinstance(ds, ExcelDataSource)
        assert ds.storage_type() == "excel"
        assert ds.config_name == "foo_bar"
        assert ds.name == "super name"
        assert ds.scope == Scope.PIPELINE
        assert ds.id is not None
        assert ds.parent_id is None
        assert ds.last_edition_date is None
        assert ds.job_ids == []
        assert not ds.is_ready_for_reading
        assert ds.path == path
        assert ds.has_header is False
        assert ds.sheet_name == sheet_names

    def test_create_with_missing_parameters(self):
        with pytest.raises(MissingRequiredProperty):
            ExcelDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"))
        with pytest.raises(MissingRequiredProperty):
            ExcelDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={})
        with pytest.raises(MissingRequiredProperty):
            ExcelDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={"path": "path"})
        with pytest.raises(MissingRequiredProperty):
            ExcelDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={"has_header": True})
        with pytest.raises(MissingRequiredProperty):
            ExcelDataSource("foo", Scope.PIPELINE, DataSourceId("ds_id"), properties={"sheet_name": "sheet_name_1"})

    def test_read_with_header(self):
        not_existing_csv = ExcelDataSource(
            "foo", Scope.PIPELINE, properties={"path": "WRONG.csv", "has_header": True, "sheet_name": "sheet_name_1"}
        )
        with pytest.raises(NoData):
            not_existing_csv.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

        # Create ExcelDataSource without exposed_type (Default is pandas.DataFrame)
        excel_data_source_as_pandas = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": True, "sheet_name": "sheet_name_1"}
        )

        data_pandas = excel_data_source_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 5

        # Create the same ExcelDataSource but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        excel_data_source_as_custom_object = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": True, "exposed_type": MyCustomObject, "sheet_name": "sheet_name_1"},
        )

        data_custom = excel_data_source_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 5

        for (index, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
            assert isinstance(row_custom, MyCustomObject)
            assert row_pandas["id"] == row_custom.id
            assert row_pandas["integer"] == row_custom.integer
            assert row_pandas["text"] == row_custom.text

    def test_read_without_header(self):
        not_existing_excel = ExcelDataSource(
            "foo", Scope.PIPELINE, properties={"path": "WRONG.csv", "has_header": False, "sheet_name": "sheet_name_1"}
        )
        with pytest.raises(NoData):
            not_existing_excel.read()
        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        # Create CSVDataSource without exposed_type (Default is pandas.DataFrame)
        excel_data_source_as_pandas = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "sheet_name": "sheet_name_1"}
        )
        data_pandas = excel_data_source_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 6

        # Create the same CSVDataSource but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        excel_data_source_as_custom_object = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={
                "path": path,
                "has_header": False,
                "sheet_name": "sheet_name_1",
                "exposed_type": MyCustomObject,
            },
        )

        data_custom = excel_data_source_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 6

        for (index, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
            assert isinstance(row_custom, MyCustomObject)
            assert row_pandas[0] == row_custom.id
            assert row_pandas[1] == row_custom.integer
            assert row_pandas[2] == row_custom.text

    @pytest.mark.parametrize(
        "content,columns",
        [
            ([{"a": 11, "b": 22, "c": 33}, {"a": 44, "b": 55, "c": 66}], None),
            ([[11, 22, 33], [44, 55, 66]], None),
            ([[11, 22, 33], [44, 55, 66]], ["e", "f", "g"]),
        ],
    )
    def test_write(self, excel_file, default_data_frame, content, columns):
        excel_ds = ExcelDataSource(
            "foo", Scope.PIPELINE, properties={"path": excel_file, "has_header": True, "sheet_name": "sheet_name_1"}
        )
        assert np.array_equal(excel_ds.read().values, default_data_frame.values)
        if not columns:
            excel_ds.write(content)
            df = pd.DataFrame(content)
        else:
            excel_ds.write_with_column_names(content, columns)
            df = pd.DataFrame(content, columns=columns)
        print(f"excel_ds: \n{excel_ds.read()}")
        print(f"df: \n{df.values}")

        assert np.array_equal(excel_ds.read().values, df.values)

        excel_ds.write(None)
        assert len(excel_ds.read()) == 0
