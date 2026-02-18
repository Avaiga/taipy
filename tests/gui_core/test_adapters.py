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

import math
import sys
from datetime import date, datetime
from unittest.mock import Mock, patch

import pandas as pd

from taipy import Scope
from taipy.core import Cycle, DataNode, Scenario
from taipy.core.common.frequency import Frequency
from taipy.core.data import JSONDataNode
from taipy.core.data.pickle import PickleDataNode
from taipy.core.reason import Reason, ReasonCollection
from taipy.gui.utils import _TaipyBase
from taipy.gui_core._adapters import (
    _adapt_type,
    _EntityType,
    _filter_iterable,
    _filter_value,
    _get_entity_property,
    _get_reason,
    _GuiCoreDatanodeAdapter,
    _GuiCoreDatanodeFilter,
    _GuiCoreDatanodeSort,
    _GuiCoreDoNotUpdate,
    _GuiCoreScenarioAdapter,
    _GuiCoreScenarioDagAdapter,
    _GuiCoreScenarioFilter,
    _GuiCoreScenarioNoUpdate,
    _GuiCoreScenarioProperties,
    _GuiCoreScenarioSort,
    _invoke_action,
    _is_debugging,
    _operators,
)


class TestGetReason:
    def test_get_reason_with_valid_reason_collection(self):
        rc = ReasonCollection()
        result = _get_reason(rc, "Test message")
        assert result == ""

    def test_get_reason_with_invalid_reason_collection(self):
        rc = ReasonCollection()
        rc._add_reason("entity_id", Reason("test reason"))
        result = _get_reason(rc, "Test message")
        assert result == "Test message: test reason."


class TestGuiCoreDoNotUpdate:
    def test_repr_with_get_label(self):
        obj = _GuiCoreDoNotUpdate()
        obj.get_label = Mock(return_value="Test Label")  # pyright: ignore[reportAttributeAccessIssue]
        assert repr(obj) == "Test Label"

    def test_repr_without_get_label(self):
        obj = _GuiCoreDoNotUpdate()
        result = repr(obj)
        assert "Taipy: Do not update" in result


class TestEntityType:
    def test_entity_type_values(self):
        assert _EntityType.CYCLE.value == 0
        assert _EntityType.SCENARIO.value == 1
        assert _EntityType.SEQUENCE.value == 2
        assert _EntityType.DATANODE.value == 3


class TestGuiCoreScenarioAdapter:
    def test_get_hash(self):
        assert _GuiCoreScenarioAdapter.get_hash() == _TaipyBase._HOLDER_PREFIX + "Sc"

    def test_get_with_none(self):
        adapter = _GuiCoreScenarioAdapter(None, "")
        adapter._get_data = Mock(return_value=None)  # pyright: ignore[reportAttributeAccessIssue]
        assert adapter.get() is None

    def test_get_with_scenario_in_list(self):
        scenario = Scenario("test_config", None, {})
        adapter = _GuiCoreScenarioAdapter(scenario, "")
        adapter._get_data = Mock(return_value=[scenario])  # pyright: ignore[reportAttributeAccessIssue]

        with patch("taipy.gui_core._adapters.core_get") as mock_core_get:
            with patch("taipy.gui_core._adapters.is_deletable") as mock_is_deletable:
                with patch("taipy.gui_core._adapters.is_promotable") as mock_is_promotable:
                    with patch("taipy.gui_core._adapters.is_submittable") as mock_is_submittable:
                        with patch("taipy.gui_core._adapters.is_readable") as mock_is_readable:
                            with patch("taipy.gui_core._adapters.is_editable") as mock_is_editable:
                                mock_core_get.return_value = scenario
                                mock_is_deletable.return_value = ReasonCollection()
                                mock_is_promotable.return_value = ReasonCollection()
                                mock_is_submittable.return_value = ReasonCollection()
                                mock_is_readable.return_value = ReasonCollection()
                                mock_is_editable.return_value = ReasonCollection()

                                result = adapter.get()
                                assert result is not None

    def test_get_with_exception(self):
        scenario = Scenario("test_config", None, {})
        adapter = _GuiCoreScenarioAdapter(scenario, "")
        adapter._get_data = Mock(return_value=scenario)  # pyright: ignore[reportAttributeAccessIssue]

        with patch("taipy.gui_core._adapters.core_get", side_effect=Exception("Test error")):
            with patch("taipy.gui_core._adapters._warn") as mock_warn:
                result = adapter.get()
                assert result is None
                mock_warn.assert_called_once()


class TestGuiCoreScenarioDagAdapter:
    def test_get_hash(self):
        assert _GuiCoreScenarioDagAdapter.get_hash() == _TaipyBase._HOLDER_PREFIX + "ScG"

    def test_get_entity_type_with_datanode(self):
        mock_node = Mock()
        mock_node.entity = DataNode("test_config", Scope.SCENARIO)
        mock_node.type = "Task"

        result = _GuiCoreScenarioDagAdapter.get_entity_type(mock_node)
        assert result == "DataNode"

    def test_get_entity_type_without_datanode(self):
        mock_node = Mock()
        mock_node.entity = Mock()
        mock_node.type = "Task"

        result = _GuiCoreScenarioDagAdapter.get_entity_type(mock_node)
        assert result == "Task"

    def test_get_with_exception(self):
        scenario = Scenario("test_config", None, {})
        adapter = _GuiCoreScenarioDagAdapter(scenario, "")
        adapter._get_data = Mock(return_value=scenario)  # pyright: ignore[reportAttributeAccessIssue]

        with patch("taipy.gui_core._adapters.core_get", side_effect=Exception("Test error")):
            with patch("taipy.gui_core._adapters._warn") as mock_warn:
                result = adapter.get()
                assert result is None
                mock_warn.assert_called_once()


class TestGuiCoreScenarioNoUpdate:
    def test_get_hash(self):
        assert _GuiCoreScenarioNoUpdate.get_hash() == _TaipyBase._HOLDER_PREFIX + "ScN"


class TestGuiCoreDatanodeAdapter:
    def test_get_hash(self):
        assert _GuiCoreDatanodeAdapter.get_hash() == _TaipyBase._HOLDER_PREFIX + "Dn"

    def test_is_tabular_data_with_tabular_mixin(self):
        from taipy.core.data._tabular_datanode_mixin import _TabularDataNodeMixin

        mock_dn = Mock(spec=_TabularDataNodeMixin)
        result = _GuiCoreDatanodeAdapter._is_tabular_data(mock_dn, None)
        assert result is True

    def test_is_tabular_data_with_dataframe(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = _GuiCoreDatanodeAdapter._is_tabular_data(dn, df)
        assert result is True

    def test_is_tabular_data_with_series(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        series = pd.Series([1, 2, 3])
        result = _GuiCoreDatanodeAdapter._is_tabular_data(dn, series)
        assert result is True

    def test_is_tabular_data_with_list(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        result = _GuiCoreDatanodeAdapter._is_tabular_data(dn, [1, 2, 3])
        assert result is True

    def test_is_tabular_data_with_tuple(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        result = _GuiCoreDatanodeAdapter._is_tabular_data(dn, (1, 2, 3))
        assert result is True

    def test_is_tabular_data_with_dict(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        result = _GuiCoreDatanodeAdapter._is_tabular_data(dn, {"a": 1})
        assert result is True

    def test_is_tabular_data_with_json_datanode(self):
        mock_dn = Mock(spec=JSONDataNode)
        result = _GuiCoreDatanodeAdapter._is_tabular_data(mock_dn, {"a": 1})
        assert result is False

    def test_get_with_exception(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        adapter = _GuiCoreDatanodeAdapter(dn, "")
        adapter._get_data = Mock(return_value=dn)  # pyright: ignore[reportAttributeAccessIssue]

        with patch("taipy.gui_core._adapters.core_get", side_effect=Exception("Test error")):
            with patch("taipy.gui_core._adapters._warn") as mock_warn:
                result = adapter.get()
                assert result is None
                mock_warn.assert_called_once()


class TestFilterValue:
    def test_filter_value_with_none_base_val_string(self):
        result = _filter_value(None, _operators["=="], "test")
        assert result is False

    def test_filter_value_with_none_base_val_number(self):
        result = _filter_value(None, _operators["=="], 5)
        assert result is False

    def test_filter_value_with_datetime(self):
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = _filter_value(dt, _operators["=="], "2023-01-01T12:00:00")
        assert result is True

    def test_filter_value_with_date(self):
        d = date(2023, 1, 1)
        result = _filter_value(d, _operators["=="], "2023-01-01")
        assert result is True

    def test_filter_value_case_insensitive(self):
        result = _filter_value("Test", _operators["=="], "test", match_case=False)
        assert result is True

    def test_filter_value_case_sensitive(self):
        result = _filter_value("Test", _operators["=="], "test", match_case=True)
        assert result is False

    def test_filter_value_with_adapt_function(self):
        def adapt_fn(base, val):
            return int(val)

        result = _filter_value(5, _operators["=="], "5", adapt=adapt_fn)
        assert result is True


class TestAdaptType:
    def test_adapt_type_with_matching_types(self):
        result = _adapt_type(5, 10)
        assert result == 10

    def test_adapt_type_with_string_to_int(self):
        result = _adapt_type(5, "10")
        assert result == 10

    def test_adapt_type_with_string_to_float(self):
        result = _adapt_type(5.5, "10.5")
        assert result == 10.5

    def test_adapt_type_with_boolean_true(self):
        result = _adapt_type(True, "true")
        assert result is True

    def test_adapt_type_with_boolean_false(self):
        result = _adapt_type(True, "false")
        assert result is False

    def test_adapt_type_with_invalid_conversion(self):
        result = _adapt_type(5, "not_a_number")
        assert result == "not_a_number"


class TestFilterIterable:
    def test_filter_iterable_with_contains_operator(self):
        result = _filter_iterable([1, 2, 3], _operators["contains"], 2)
        assert result is True

    def test_filter_iterable_with_contains_operator_not_found(self):
        result = _filter_iterable([1, 2, 3], _operators["contains"], 5)
        assert result is False

    def test_filter_iterable_with_datetime_list(self):
        dt_list = [datetime(2023, 1, 1), datetime(2023, 1, 2)]
        result = _filter_iterable(dt_list, _operators["contains"], "2023-01-01T00:00:00")
        assert result is True

    def test_filter_iterable_with_equality_operator(self):
        result = _filter_iterable([1, 2, 3], _operators["=="], 2)
        assert result is True


class TestInvokeAction:
    def test_invoke_action_with_none_entity(self):
        result = _invoke_action(None, "col", "str", False, "==", "value")
        assert result is False

    def test_invoke_action_with_string_column(self):
        mock_entity = Mock()
        mock_entity.test_value = "test"

        result = _invoke_action(mock_entity, "test_value", "str", False, "==", "test")
        assert result is True

    def test_invoke_action_with_datanode_value(self):
        mock_entity = Mock()
        mock_datanode = Mock(spec=DataNode)
        mock_datanode.read.return_value = "test_value"
        mock_entity.dn = mock_datanode

        result = _invoke_action(mock_entity, "dn", "str", False, "==", "test_value")
        assert result is True

    def test_invoke_action_with_iterable_value(self):
        mock_entity = Mock()
        mock_entity.tags = ["tag1", "tag2", "tag3"]

        result = _invoke_action(mock_entity, "tags", "str", False, "contains", "tag2")
        assert result is True

    def test_invoke_action_with_any_type_not_found(self):
        mock_entity = Mock()
        mock_entity.properties = {}

        result = _invoke_action(mock_entity, "missing_prop", "any", False, "!=", "value")
        assert result is True

    def test_invoke_action_with_any_type_not_found_equal(self):
        mock_entity = Mock()
        mock_entity.properties = {}

        result = _invoke_action(mock_entity, "missing_prop", "any", False, "==", "value")
        assert result is False

    def test_invoke_action_with_exception(self):
        mock_entity = Mock()
        mock_entity.test_value = Mock(side_effect=Exception("Test error"))

        result = _invoke_action(mock_entity, "test_value", "str", False, "==", "test")
        assert result is False


class TestGetEntityProperty:
    def test_get_entity_property_with_simple_attribute(self):
        scenario = Scenario("test_config", None, {})

        sort_fn = _get_entity_property("config_id", Scenario)
        result = sort_fn(scenario)
        assert result == "test_config"

    def test_get_entity_property_with_method(self):
        scenario = Scenario("test_config", None, {})

        sort_fn = _get_entity_property("get_simple_label()", Scenario)
        result = sort_fn(scenario)
        assert isinstance(result, str)

    def test_get_entity_property_with_datetime(self):
        scenario = Scenario("test_config", None, {}, creation_date=datetime(2023, 1, 1, 12, 0, 0))

        sort_fn = _get_entity_property("creation_date", Scenario)
        result = sort_fn(scenario)
        assert result == "2023-01-01T12:00:00"

    def test_get_entity_property_with_wrong_type(self):
        datanode = PickleDataNode("test_config", Scope.SCENARIO)

        sort_fn = _get_entity_property("config_id", Scenario)
        result = sort_fn(datanode)
        assert result == "Z"

    def test_get_entity_property_with_cycle(self):
        cycle = Cycle(
            Frequency.DAILY, {}, datetime(2023, 1, 1), datetime(2023, 12, 31), datetime(2023, 12, 31), "test_cycle"
        )

        sort_fn = _get_entity_property("creation_date", Cycle)
        result = sort_fn(cycle)
        assert isinstance(result, str)

    def test_get_entity_property_with_exception(self):
        scenario = Scenario("test_config", None, {})

        sort_fn = _get_entity_property("non_existent_attr", Scenario)
        result = sort_fn(scenario)
        assert result == "Z"


class TestGuiCoreScenarioProperties:
    def test_is_datanode_property_with_dot(self):
        result = _GuiCoreScenarioProperties.is_datanode_property("datanode.property")
        assert result is True

    def test_is_datanode_property_without_dot(self):
        result = _GuiCoreScenarioProperties.is_datanode_property("simple_property")
        assert result is False

    def test_is_datanode_property_with_known_property(self):
        result = _GuiCoreScenarioProperties.is_datanode_property("cycle.name")
        assert result is False


class TestGuiCoreScenarioFilter:
    def test_get_hash(self):
        assert _GuiCoreScenarioFilter.get_hash() == _TaipyBase._HOLDER_PREFIX + "ScF"

    def test_full_desc(self):
        assert _GuiCoreScenarioFilter.full_desc() is True

    def test_get_default_list(self):
        result = _GuiCoreScenarioFilter.get_default_list()
        assert isinstance(result, list)
        assert len(result) > 0


class TestGuiCoreScenarioSort:
    def test_get_hash(self):
        assert _GuiCoreScenarioSort.get_hash() == _TaipyBase._HOLDER_PREFIX + "ScS"

    def test_full_desc(self):
        assert _GuiCoreScenarioSort.full_desc() is False

    def test_get_default_list(self):
        result = _GuiCoreScenarioSort.get_default_list()
        assert isinstance(result, list)
        assert len(result) > 0


class TestGuiCoreDatanodeFilter:
    def test_get_hash(self):
        assert _GuiCoreDatanodeFilter.get_hash() == _TaipyBase._HOLDER_PREFIX + "DnF"

    def test_full_desc(self):
        assert _GuiCoreDatanodeFilter.full_desc() is True

    def test_get_default_list(self):
        result = _GuiCoreDatanodeFilter.get_default_list()
        assert isinstance(result, list)
        assert len(result) > 0


class TestGuiCoreDatanodeSort:
    def test_get_hash(self):
        assert _GuiCoreDatanodeSort.get_hash() == _TaipyBase._HOLDER_PREFIX + "DnS"

    def test_full_desc(self):
        assert _GuiCoreDatanodeSort.full_desc() is False

    def test_get_default_list(self):
        result = _GuiCoreDatanodeSort.get_default_list()
        assert isinstance(result, list)
        assert len(result) > 0


class TestIsDebugging:
    def test_is_debugging_false(self):
        with patch.object(sys, "gettrace", return_value=None):
            result = _is_debugging()
            assert result is False

    def test_is_debugging_true(self):
        with patch.object(sys, "gettrace", return_value=Mock()):
            result = _is_debugging()
            assert result is True

    def test_is_debugging_no_gettrace(self):
        original_gettrace = getattr(sys, "gettrace", None)
        if hasattr(sys, "gettrace"):
            delattr(sys, "gettrace")

        result = _is_debugging()
        assert result is False

        if original_gettrace is not None:
            sys.gettrace = original_gettrace


class TestOperators:
    def test_operators_dict_contains_all_operators(self):
        assert "==" in _operators
        assert "!=" in _operators
        assert "<" in _operators
        assert "<=" in _operators
        assert ">" in _operators
        assert ">=" in _operators
        assert "contains" in _operators

    def test_operators_work_correctly(self):
        assert _operators["=="](5, 5) is True
        assert _operators["!="](5, 3) is True
        assert _operators["<"](3, 5) is True
        assert _operators["<="](5, 5) is True
        assert _operators[">"](5, 3) is True
        assert _operators[">="](5, 5) is True
        assert _operators["contains"]([1, 2, 3], 2) is True


class TestGuiCoreDatanodeAdapterGetData:
    def test_get_data_without_last_edit_date(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)
        dn._last_edit_date = None

        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[0] is None
        assert result[1] is None
        assert result[2] is None
        assert "Data unavailable" in result[3]

    def test_get_data_with_tabular_mixin(self):
        from taipy.core.data._tabular_datanode_mixin import _TabularDataNodeMixin

        mock_dn = Mock(spec=_TabularDataNodeMixin)
        mock_dn._last_edit_date = datetime.now()

        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(mock_dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result == (None, None, True, None)

    def test_get_data_with_float_nan(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO, properties={"default_data": math.nan})

        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[0] is None
        assert result[1] == "float"

    def test_get_data_with_int_value(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO, properties={"default_data": 42})

        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[0] == 42
        assert result[1] == "int"

    def test_get_data_with_string_value(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO, properties={"default_data": "test string"})

        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[0] == "test string"
        assert result[1] == "str"

    def test_get_data_with_date_value(self):
        test_date = datetime(2023, 1, 1, 12, 0, 0)
        dn = PickleDataNode("test_config", Scope.SCENARIO, properties={"default_data": test_date})
        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[0] == test_date
        assert result[1] == "date"

    def test_get_data_with_dataframe(self):
        df = pd.DataFrame({"a": [1, 2, 3]})
        dn = PickleDataNode("test_config", Scope.SCENARIO, properties={"default_data": df})
        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[2] is True

    def test_get_data_with_read_exception(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO)

        adapter = _GuiCoreDatanodeAdapter(None, "")

        with patch.object(dn, "read", side_effect=Exception("Read error")):
            result = adapter._GuiCoreDatanodeAdapter__get_data(dn)  # pyright: ignore[reportAttributeAccessIssue]

            assert result[0] is None
            assert result[1] is None
            assert result[2] is None
            assert "Data unavailable for test_config" in result[3]

    def test_get_data_with_json_datanode(self):
        mock_dn = Mock(spec=JSONDataNode)
        mock_dn._last_edit_date = datetime.now()
        mock_dn.read.return_value = {"key": "value"}
        mock_dn.get_simple_label.return_value = "test_json"

        adapter = _GuiCoreDatanodeAdapter(None, "")
        result = adapter._GuiCoreDatanodeAdapter__get_data(mock_dn)  # pyright: ignore[reportAttributeAccessIssue]

        assert result[4] is True


class TestGuiCoreDatanodeAdapterGet:
    def test_get_with_datanode_list(self):
        dn = PickleDataNode("test_config", Scope.SCENARIO, properties={"default_data": 42})

        adapter = _GuiCoreDatanodeAdapter(dn, "")

        with patch("taipy.gui_core._adapters.core_get", return_value=dn):
            with patch("taipy.gui_core._adapters.is_readable", return_value=ReasonCollection()):
                with patch("taipy.gui_core._adapters.is_editable", return_value=ReasonCollection()):
                    result = adapter.get()

                    assert result is not None
                    assert result[0] == dn.id

    def test_get_with_scenario_owner(self):
        scenario = Scenario("scenario_config", None, {})
        dn = PickleDataNode("test_config", Scope.SCENARIO, owner_id=scenario.id, properties={"default_data": 42})

        adapter = _GuiCoreDatanodeAdapter(dn, "")

        with patch("taipy.gui_core._adapters.core_get") as mock_core_get:

            def core_get_side_effect(entity_id):
                if entity_id == dn.id:
                    return dn
                if entity_id == scenario.id:
                    return scenario
                return None

            mock_core_get.side_effect = core_get_side_effect

            with patch("taipy.gui_core._adapters.is_readable", return_value=ReasonCollection()):
                with patch("taipy.gui_core._adapters.is_editable", return_value=ReasonCollection()):
                    result = adapter.get()

                    assert result is not None
                    assert result[8] == _EntityType.SCENARIO.value

    def test_get_with_cycle_owner(self):
        cycle = Cycle(
            Frequency.DAILY, {}, datetime(2023, 1, 1), datetime(2023, 12, 31), datetime(2023, 12, 31), "test_cycle"
        )
        dn = PickleDataNode("test_config", Scope.SCENARIO, owner_id=cycle.id, properties={"default_data": 42})

        adapter = _GuiCoreDatanodeAdapter(dn, "")

        with patch("taipy.gui_core._adapters.core_get") as mock_core_get:

            def core_get_side_effect(entity_id):
                if entity_id == dn.id:
                    return dn
                if entity_id == cycle.id:
                    return cycle
                return None

            mock_core_get.side_effect = core_get_side_effect

            with patch("taipy.gui_core._adapters.is_readable", return_value=ReasonCollection()):
                with patch("taipy.gui_core._adapters.is_editable", return_value=ReasonCollection()):
                    result = adapter.get()

                    assert result is not None
                    assert result[8] == _EntityType.CYCLE.value
