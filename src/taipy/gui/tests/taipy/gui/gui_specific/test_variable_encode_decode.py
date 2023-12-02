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

from taipy.gui.utils._variable_directory import _MODULE_NAME_MAP, _variable_decode, _variable_encode


def test_variable_encode_decode():
    assert _variable_encode("x", "module") == "x_TPMDL_0"
    assert _MODULE_NAME_MAP[0] == "module"
    assert _variable_decode("x_TPMDL_0") == ("x", "module")
    assert _variable_encode("x", None) == "x"
    assert _variable_decode("x") == ("x", None)
    assert _variable_encode("TpExPr_x", "module1") == "TpExPr_x_TPMDL_1"
    assert _MODULE_NAME_MAP[1] == "module1"
    assert _variable_decode("TpExPr_x_TPMDL_1") == ("x", "module1")
