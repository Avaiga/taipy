# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from taipy.config import Config
from taipy.core.common.warn_if_inputs_not_ready import _warn_if_inputs_not_ready
from taipy.core.data._data_manager_factory import _DataManagerFactory


def test_warn_inputs_all_not_ready(caplog):
    one = Config.configure_data_node("one")
    two = Config.configure_data_node("two")
    three = Config.configure_data_node("three")
    data_nodes = _DataManagerFactory._build_manager()._bulk_get_or_create({one, two, three}).values()

    _warn_if_inputs_not_ready(data_nodes)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in data_nodes
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)


def test_warn_inputs_all_ready(caplog):
    one = Config.configure_data_node("one", default_data=1)
    two = Config.configure_data_node("two", default_data=2)
    three = Config.configure_data_node("three", default_data=3)
    data_nodes = _DataManagerFactory._build_manager()._bulk_get_or_create({one, two, three}).values()

    _warn_if_inputs_not_ready(data_nodes)

    stdout = caplog.text
    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in data_nodes
    ]
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def test_warn_inputs_one_ready(caplog):
    one = Config.configure_data_node("one", default_data=1)
    two = Config.configure_data_node("two")
    three = Config.configure_data_node("three")
    data_nodes = _DataManagerFactory._build_manager()._bulk_get_or_create({one, two, three})

    _warn_if_inputs_not_ready(data_nodes.values())

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in [data_nodes[two], data_nodes[three]]
    ]

    not_expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in [data_nodes[one]]
    ]

    assert all(expected_output in stdout for expected_output in expected_outputs)
    assert all(expected_output not in stdout for expected_output in not_expected_outputs)


def test_submit_task_with_input_dn_wrong_file_path(caplog):
    csv_dn_cfg = Config.configure_csv_data_node("wrong_csv_file_path", default_path="wrong_path.csv")
    excel_dn_cfg = Config.configure_excel_data_node("wrong_excel_file_path", default_path="wrong_path.xlsx")
    json_dn_cfg = Config.configure_json_data_node("wrong_json_file_path", default_path="wrong_path.json")
    pickle_dn_cfg = Config.configure_pickle_data_node("wrong_pickle_file_path", default_path="wrong_path.pickle")
    parquet_dn_cfg = Config.configure_parquet_data_node("wrong_parquet_file_path", default_path="wrong_path.parquet")
    input_dn_cfgs = [csv_dn_cfg, excel_dn_cfg, json_dn_cfg, pickle_dn_cfg, parquet_dn_cfg]

    dn_manager = _DataManagerFactory._build_manager()
    dns = [dn_manager._bulk_get_or_create([input_dn_cfg])[input_dn_cfg] for input_dn_cfg in input_dn_cfgs]

    _warn_if_inputs_not_ready(dns)

    stdout = caplog.text
    expected_outputs = [
        f"{input_dn.id} cannot be read because it has never been written. Hint: The data node may refer to a wrong "
        f"path : {input_dn.path} "
        for input_dn in dns
    ]
    assert all(expected_output in stdout for expected_output in expected_outputs)
