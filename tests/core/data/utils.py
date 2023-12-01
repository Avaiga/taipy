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

from src.taipy.config.common.scope import Scope
from src.taipy.core.data.data_node import DataNode
from src.taipy.core.data.in_memory import InMemoryDataNode


class FakeDataNode(InMemoryDataNode):
    read_has_been_called = 0
    write_has_been_called = 0

    def __init__(self, config_id, **kwargs):
        scope = kwargs.pop("scope", Scope.SCENARIO)
        super().__init__(config_id=config_id, scope=scope, **kwargs)

    def _read(self, query=None):
        self.read_has_been_called += 1

    def _write(self, data):
        self.write_has_been_called += 1

    @classmethod
    def storage_type(cls) -> str:
        return "fake_inmemory"

    write = DataNode.write  # Make sure that the writing behavior comes from DataNode


class FakeDataframeDataNode(DataNode):
    COLUMN_NAME_1 = "a"
    COLUMN_NAME_2 = "b"

    def __init__(self, config_id, default_data_frame, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = default_data_frame

    def _read(self):
        return self.data

    @classmethod
    def storage_type(cls) -> str:
        return "fake_df_dn"


class FakeNumpyarrayDataNode(DataNode):
    def __init__(self, config_id, default_array, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = default_array

    def _read(self):
        return self.data

    @classmethod
    def storage_type(cls) -> str:
        return "fake_np_dn"


class FakeListDataNode(DataNode):
    class Row:
        def __init__(self, value):
            self.value = value

    def __init__(self, config_id, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = [self.Row(i) for i in range(10)]

    def _read(self):
        return self.data

    @classmethod
    def storage_type(cls) -> str:
        return "fake_list_dn"


class CustomClass:
    def __init__(self, a, b):
        self.a = a
        self.b = b


class FakeCustomDataNode(DataNode):
    def __init__(self, config_id, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = [CustomClass(i, i * 2) for i in range(10)]

    def _read(self):
        return self.data


class FakeMultiSheetExcelDataFrameDataNode(DataNode):
    def __init__(self, config_id, default_data_frame, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = {
            "Sheet1": default_data_frame,
            "Sheet2": default_data_frame,
        }

    def _read(self):
        return self.data


class FakeMultiSheetExcelCustomDataNode(DataNode):
    def __init__(self, config_id, **kwargs):
        super().__init__(config_id, **kwargs)
        self.data = {
            "Sheet1": [CustomClass(i, i * 2) for i in range(10)],
            "Sheet2": [CustomClass(i, i * 2) for i in range(10)],
        }

    def _read(self):
        return self.data
