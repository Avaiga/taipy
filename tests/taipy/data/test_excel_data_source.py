import os
import pathlib
from typing import Dict

import numpy as np
import pandas as pd
import pytest

from taipy.common.alias import DataSourceId
from taipy.data.excel import ExcelDataSource
from taipy.data.scope import Scope
from taipy.exceptions import MissingRequiredProperty
from taipy.exceptions.data_source import NoData, NonExistingExcelSheet


class TestExcelDataSource:
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

    def test_read_with_header(self):
        not_existing_excel = ExcelDataSource(
            "foo", Scope.PIPELINE, properties={"path": "WRONG.xlsx", "has_header": True}
        )
        with pytest.raises(NoData):
            not_existing_excel.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

        # Create ExcelDataSource without exposed_type (Default is pandas.DataFrame)
        excel_data_source_as_pandas = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": True}
        )

        data_pandas = excel_data_source_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 5
        assert np.array_equal(data_pandas.to_numpy(), pd.read_excel(path).to_numpy())

        # Create ExcelDataSource with numpy exposed_type
        excel_data_source_as_numpy = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": True, "exposed_type": "numpy"}
        )

        data_numpy = excel_data_source_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 5
        assert np.array_equal(data_numpy, pd.read_excel(path).to_numpy())

        # Create the same ExcelDataSource but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        non_existing_sheet_name_custom = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": True, "sheet_name": "abc", "exposed_type": MyCustomObject},
        )
        with pytest.raises(NonExistingExcelSheet):
            non_existing_sheet_name_custom.read()

        excel_data_source_as_custom_object = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": True, "exposed_type": MyCustomObject},
        )

        data_custom = excel_data_source_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 5

        for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
            assert isinstance(row_custom, MyCustomObject)
            assert row_pandas["id"] == row_custom.id
            assert row_pandas["integer"] == row_custom.integer
            assert row_pandas["text"] == row_custom.text

    def test_read_without_header(self):
        not_existing_excel = ExcelDataSource(
            "foo", Scope.PIPELINE, properties={"path": "WRONG.xlsx", "has_header": False}
        )
        with pytest.raises(NoData):
            not_existing_excel.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")

        # Create ExcelDataSource without exposed_type (Default is pandas.DataFrame)
        excel_data_source_as_pandas = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False}
        )
        data_pandas = excel_data_source_as_pandas.read()
        assert isinstance(data_pandas, pd.DataFrame)
        assert len(data_pandas) == 6
        assert np.array_equal(data_pandas.to_numpy(), pd.read_excel(path, header=None).to_numpy())

        # Create ExcelDataSource with numpy exposed_type
        excel_data_source_as_numpy = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "exposed_type": "numpy"}
        )

        data_numpy = excel_data_source_as_numpy.read()
        assert isinstance(data_numpy, np.ndarray)
        assert len(data_numpy) == 6
        assert np.array_equal(data_numpy, pd.read_excel(path, header=None).to_numpy())

        # Create the same ExcelDataSource but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        non_existing_sheet_name_custom = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": False, "sheet_name": "abc", "exposed_type": MyCustomObject},
        )
        with pytest.raises(NonExistingExcelSheet):
            non_existing_sheet_name_custom.read()

        excel_data_source_as_custom_object = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={
                "path": path,
                "has_header": False,
                "exposed_type": MyCustomObject,
            },
        )

        data_custom = excel_data_source_as_custom_object.read()
        assert isinstance(data_custom, list)
        assert len(data_custom) == 6

        for (_, row_pandas), row_custom in zip(data_pandas.iterrows(), data_custom):
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
            "foo", Scope.PIPELINE, properties={"path": excel_file, "has_header": True, "sheet_name": "Sheet1"}
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

    def test_read_multi_sheet_with_header(self):
        not_existing_excel = ExcelDataSource(
            "foo",
            Scope.PIPELINE,
            properties={"path": "WRONG.xlsx", "has_header": True, "sheet_name": ["sheet_name_1", "sheet_name_2"]},
        )
        with pytest.raises(NoData):
            not_existing_excel.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        sheet_names = ["Sheet1", "Sheet2"]

        # Create ExcelDataSource without exposed_type (Default is pandas.DataFrame)
        excel_data_source_as_pandas = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": True, "sheet_name": sheet_names}
        )

        data_pandas = excel_data_source_as_pandas.read()
        assert isinstance(data_pandas, Dict)
        assert len(data_pandas) == 2
        assert all(
            len(data_pandas[sheet_name] == 5) and isinstance(data_pandas[sheet_name], pd.DataFrame)
            for sheet_name in sheet_names
        )
        assert list(data_pandas.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert np.array_equal(
                data_pandas[sheet_name].to_numpy(), pd.read_excel(path, sheet_name=sheet_name).to_numpy()
            )

        # Create ExcelDataSource with numpy exposed_type
        excel_data_source_as_numpy = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": True, "sheet_name": sheet_names, "exposed_type": "numpy"},
        )

        data_numpy = excel_data_source_as_numpy.read()
        assert isinstance(data_numpy, Dict)
        assert len(data_numpy) == 2
        assert all(
            len(data_numpy[sheet_name] == 5) and isinstance(data_numpy[sheet_name], np.ndarray)
            for sheet_name in sheet_names
        )
        assert list(data_numpy.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert np.array_equal(data_pandas[sheet_name], pd.read_excel(path, sheet_name=sheet_name).to_numpy())

        # Create the same ExcelDataSource but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        non_existing_sheet_name_custom = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={
                "path": path,
                "has_header": True,
                "sheet_name": ["Sheet1", "xyz"],
                "exposed_type": MyCustomObject,
            },
        )
        with pytest.raises(NonExistingExcelSheet):
            non_existing_sheet_name_custom.read()

        excel_data_source_as_custom_object = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": True, "sheet_name": sheet_names, "exposed_type": MyCustomObject},
        )

        data_custom = excel_data_source_as_custom_object.read()
        assert isinstance(data_custom, Dict)
        assert len(data_custom) == 2
        assert all(len(data_custom[sheet_name]) == 5 for sheet_name in sheet_names)
        assert list(data_custom.keys()) == sheet_names

        for sheet_name in sheet_names:
            sheet_data_pandas, sheet_data_custom = data_pandas[sheet_name], data_custom[sheet_name]
            for (_, row_pandas), row_custom in zip(sheet_data_pandas.iterrows(), sheet_data_custom):
                assert isinstance(row_custom, MyCustomObject)
                assert row_pandas["id"] == row_custom.id
                assert row_pandas["integer"] == row_custom.integer
                assert row_pandas["text"] == row_custom.text

    def test_read_multi_sheet_without_header(self):
        not_existing_excel = ExcelDataSource(
            "foo",
            Scope.PIPELINE,
            properties={"path": "WRONG.xlsx", "has_header": False, "sheet_name": ["sheet_name_1", "sheet_name_2"]},
        )
        with pytest.raises(NoData):
            not_existing_excel.read()

        path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample/example.xlsx")
        sheet_names = ["Sheet1", "Sheet2"]

        # Create ExcelDataSource without exposed_type (Default is pandas.DataFrame)
        excel_data_source_as_pandas = ExcelDataSource(
            "bar", Scope.PIPELINE, properties={"path": path, "has_header": False, "sheet_name": sheet_names}
        )
        data_pandas = excel_data_source_as_pandas.read()
        assert isinstance(data_pandas, Dict)
        assert len(data_pandas) == 2
        assert all(len(data_pandas[sheet_name]) == 6 for sheet_name in sheet_names)
        assert list(data_pandas.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert np.array_equal(
                data_pandas[sheet_name].to_numpy(), pd.read_excel(path, header=None, sheet_name=sheet_name).to_numpy()
            )

        # Create ExcelDataSource with numpy exposed_type
        excel_data_source_as_numpy = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={"path": path, "has_header": False, "sheet_name": sheet_names, "exposed_type": "numpy"},
        )

        data_numpy = excel_data_source_as_numpy.read()
        assert isinstance(data_numpy, Dict)
        assert len(data_numpy) == 2
        assert all(
            len(data_numpy[sheet_name] == 6) and isinstance(data_numpy[sheet_name], np.ndarray)
            for sheet_name in sheet_names
        )
        assert list(data_numpy.keys()) == sheet_names
        for sheet_name in sheet_names:
            assert np.array_equal(
                data_pandas[sheet_name], pd.read_excel(path, header=None, sheet_name=sheet_name).to_numpy()
            )

        # Create the same ExcelDataSource but with custom exposed_type
        class MyCustomObject:
            def __init__(self, id, integer, text):
                self.id = id
                self.integer = integer
                self.text = text

        non_existing_sheet_name_custom = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={
                "path": path,
                "has_header": False,
                "sheet_name": ["Sheet1", "xyz"],
                "exposed_type": MyCustomObject,
            },
        )
        with pytest.raises(NonExistingExcelSheet):
            non_existing_sheet_name_custom.read()

        excel_data_source_as_custom_object = ExcelDataSource(
            "bar",
            Scope.PIPELINE,
            properties={
                "path": path,
                "has_header": False,
                "sheet_name": sheet_names,
                "exposed_type": MyCustomObject,
            },
        )

        data_custom = excel_data_source_as_custom_object.read()
        assert isinstance(data_custom, Dict)
        assert len(data_custom) == 2
        assert all(len(data_custom[sheet_name]) == 6 for sheet_name in sheet_names)
        assert list(data_custom.keys()) == sheet_names

        for sheet_name in sheet_names:
            sheet_data_pandas, sheet_data_custom = data_pandas[sheet_name], data_custom[sheet_name]
            for (_, row_pandas), row_custom in zip(sheet_data_pandas.iterrows(), sheet_data_custom):
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
    def test_write_multi_sheet(self, excel_file_with_multi_sheet, default_multi_sheet_data_frame, content, columns):
        sheet_names = ["Sheet1", "Sheet2"]

        excel_ds = ExcelDataSource(
            "foo",
            Scope.PIPELINE,
            properties={"path": excel_file_with_multi_sheet, "has_header": True, "sheet_name": sheet_names},
        )

        for sheet_name in sheet_names:
            assert np.array_equal(excel_ds.read()[sheet_name].values, default_multi_sheet_data_frame[sheet_name].values)

        multi_sheet_content = {sheet_name: pd.DataFrame(content) for sheet_name in sheet_names}

        excel_ds.write(multi_sheet_content)
        data_pandas = excel_ds.read()

        for sheet_name in sheet_names:
            assert np.array_equal(data_pandas[sheet_name].values, multi_sheet_content[sheet_name].values)
