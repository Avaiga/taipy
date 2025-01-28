# Copyright 2021-2025 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from unittest.mock import Mock, patch

import pandas as pd

from taipy import DataNode, Gui, Scope
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.pickle import PickleDataNode
from taipy.core.reason import Reason, ReasonCollection
from taipy.gui_core._context import _GuiCoreContext

dn = PickleDataNode("dn_config_id", scope = Scope.GLOBAL)


def core_get(entity_id):
    if entity_id == dn.id:
        return dn
    return None


def is_false(entity_id):
    return ReasonCollection()._add_reason(entity_id, Reason("foo"))


def is_true(entity_id):
    return True

def fails(**kwargs):
    raise Exception("Failed")


class MockState:
    def __init__(self, **kwargs) -> None:
        self.assign = kwargs.get("assign")


class TestGuiCoreContext_update_data:

    def test_do_not_edit_tabular_data_if_not_readable(self):
        _DataManagerFactory._build_manager()._set(dn)
        with patch("taipy.gui_core._context.is_readable", side_effect=is_false):
            with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                with patch.object(DataNode, "write") as mock_write:
                    assign = self.__call_update_data()

                    mock_core_get.assert_not_called()
                    mock_write.assert_not_called()
                    assign.assert_called_once_with("error_var", f"Data node {dn.id} is not readable: foo.")

    def test_do_not_edit_tabular_data_if_not_editable(self):
        _DataManagerFactory._build_manager()._set(dn)
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_false):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data()

                        mock_core_get.assert_not_called()
                        mock_write.assert_not_called()
                        assign.assert_called_once_with("error_var", f"Data node {dn.id} is not editable: foo.")

    def test_edit_pandas_data(self):
        dn.write(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
        idx = 0
        col = "a"
        new_value = 100
        new_data = pd.DataFrame({"a": [new_value, 2, 3], "b": [4, 5, 6]})
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)

                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once()
                        # Cannot use the following line because of the pandas DataFrame comparison
                        # mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None
                        # Instead, we will compare the arguments of the call manually
                        assert mock_write.call_args_list[0].args[0].equals(new_data)
                        assert mock_write.call_args_list[0].kwargs["editor_id"] == "a_client_id"
                        assert mock_write.call_args_list[0].kwargs["comment"] is None
                        assign.assert_called_once_with("error_var", "")

    def __call_update_data(self, col=None, idx=None, new_value=None):
        mockGui = Mock(Gui)
        mockGui._get_client_id = lambda: "a_client_id"
        gui_core_context = _GuiCoreContext(mockGui)
        payload = {"user_data": {"dn_id": dn.id}, "error_id": "error_var"}
        if idx is not None:
            payload["index"] = idx
        if col is not None:
            payload["col"] = col
        if new_value is not None:
            payload["value"] = new_value
        assign = Mock()
        gui_core_context.tabular_data_edit(
            state=MockState(assign=assign),
            var_name="",
            payload=payload,
        )
        return assign

    def test_edit_pandas_wrong_idx(self):
        data = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        dn.write(data)
        idx = 5
        col = "a"
        new_value = 100
        new_data = data.copy()
        new_data.at[idx, col] = new_value
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:

                        assign = self.__call_update_data(col, idx, new_value)

                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once()
                        # Cannot use the following line because of the pandas DataFrame comparison
                        # mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None
                        # Instead, we will compare the arguments of the call manually
                        assert mock_write.call_args_list[0].args[0].equals(new_data)
                        assert mock_write.call_args_list[0].kwargs["editor_id"] == "a_client_id"
                        assert mock_write.call_args_list[0].kwargs["comment"] is None
                        assign.assert_called_once_with("error_var", "")

    def test_edit_pandas_wrong_col(self):
        data = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        dn.write(data)
        idx = 0
        col = "c"
        new_value = 100
        new_data = data.copy()
        new_data.at[idx, col] = new_value
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once()
                        # Cannot use the following line because of the pandas DataFrame comparison
                        # mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None
                        # Instead, we will compare the arguments of the call manually
                        assert mock_write.call_args_list[0].args[0].equals(new_data)
                        assert mock_write.call_args_list[0].kwargs["editor_id"] == "a_client_id"
                        assert mock_write.call_args_list[0].kwargs["comment"] is None
                        assign.assert_called_once_with("error_var", "")

    def test_edit_pandas_series(self):
        data = pd.Series([1, 2, 3])
        dn.write(data)
        idx = 0
        col = "WHATEVER"
        new_value = 100
        new_data = pd.Series([100, 2, 3])
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once()
                        # Cannot use the following line because of the pandas Series comparison
                        # mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None
                        # Instead, we will compare the arguments of the call manually
                        assert mock_write.call_args_list[0].args[0].equals(new_data)
                        assert mock_write.call_args_list[0].kwargs["editor_id"] == "a_client_id"
                        assert mock_write.call_args_list[0].kwargs["comment"] is None
                        assign.assert_called_once_with("error_var", "")

    def test_edit_pandas_series_wrong_idx(self):
        data = pd.Series([1, 2, 3])
        dn.write(data)
        idx = 5
        col = "WHATEVER"
        new_value = 100
        new_data = data.copy()
        new_data.at[idx] = new_value
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once()
                        # Cannot use the following line because of the pandas Series comparison
                        # mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None
                        # Instead, we will compare the arguments of the call manually
                        assert mock_write.call_args_list[0].args[0].equals(new_data)
                        assert mock_write.call_args_list[0].kwargs["editor_id"] == "a_client_id"
                        assert mock_write.call_args_list[0].kwargs["comment"] is None
                        assign.assert_called_once_with("error_var", "")

    def test_edit_dict(self):
        data = {"a": [1, 2, 3], "b": [4, 5, 6]}
        dn.write(data)
        idx = 0
        col = "a"
        new_value = 100
        new_data = {"a": [100, 2, 3], "b": [4, 5, 6]}
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None)
                        assign.assert_called_once_with("error_var", "")

    def test_edit_dict_wrong_idx(self):
        data = {"a": [1, 2, 3], "b": [4, 5, 6]}
        dn.write(data)
        idx = 5
        col = "a"
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating data node tabular value. list assignment index out of range")

    def test_edit_dict_wrong_col(self):
        data = {"a": [1, 2, 3], "b": [4, 5, 6]}
        dn.write(data)
        idx = 0
        col = "c"
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating Data node: dict values must be list or tuple.")

    def test_edit_dict_of_tuples(self):
        data = {"a": (1, 2, 3), "b": (4, 5, 6)}
        dn.write(data)
        idx = 0
        col = "a"
        new_value = 100
        new_data = {"a": (100, 2, 3), "b": (4, 5, 6)}
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None)
                        assign.assert_called_once_with("error_var", "")

    def test_edit_dict_of_tuples_wrong_idx(self):
        data = {"a": (1, 2, 3), "b": (4, 5, 6)}
        dn.write(data)
        idx = 5
        col = "a"
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating data node tabular value. list assignment index out of range")

    def test_edit_dict_of_tuples_wrong_col(self):
        data = {"a": (1, 2, 3), "b": (4, 5, 6)}
        dn.write(data)
        idx = 0
        col = "c"
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating Data node: dict values must be list or tuple.")

    def test_edit_wrong_dict(self):
        data = {"a": 1, "b": 2}
        dn.write(data)
        idx = 0
        col = "a"
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating Data node: dict values must be list or tuple.")

    def test_edit_list(self):
        data = [[1, 2, 3], [4, 5, 6]]
        dn.write(data)
        idx = 0
        col = 1
        new_value = 100
        new_data = [[1, 100, 3], [4, 5, 6]]
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None)
                        assign.assert_called_once_with("error_var", "")

    def test_edit_list_wrong_idx(self):
        data = [[1, 2, 3], [4, 5, 6]]
        dn.write(data)
        idx = 5
        col = 0
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating data node tabular value. list index out of range")

    def test_edit_list_wrong_col(self):
        data = [[1, 2, 3], [4, 5, 6]]
        dn.write(data)
        idx = 0
        col = 5
        new_value = 100
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_not_called()
                        assign.assert_called_once_with(
                            "error_var",
                            "Error updating data node tabular value. list assignment index out of range")

    def test_edit_tuple(self):
        data = ([1, 2, 3], [4, 5, 6])
        dn.write(data)
        idx = 0
        col = 1
        new_value = 100
        new_data = ([1, 100, 3], [4, 5, 6])
        with patch("taipy.gui_core._context.is_readable", side_effect=is_true):
            with patch("taipy.gui_core._context.is_editable", side_effect=is_true):
                with patch("taipy.gui_core._context.core_get", side_effect=core_get) as mock_core_get:
                    with patch.object(DataNode, "write") as mock_write:
                        assign = self.__call_update_data(col, idx, new_value)
                        mock_core_get.assert_called_once_with(dn.id)
                        mock_write.assert_called_once_with(new_data, editor_id="a_client_id", comment=None)
                        assign.assert_called_once_with("error_var", "")
