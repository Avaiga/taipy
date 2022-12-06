# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from src.taipy.core.data._data_model import _DataNodeModel
from taipy.config.common.scope import Scope


class TestDataModel:
    def test_deprecated_properties(self):
        model = _DataNodeModel.from_dict(
            {
                "id": "id",
                "config_id": "config_id",
                "scope": repr(Scope.PIPELINE),
                "storage_type": "pickle",
                "name": "name",
                "parent_id": "owner_id",
                "parent_ids": ["parent_id"],
                "last_edition_date": "2020-01-01T00:00:00",
                "read_fct_name": "read_fct_name",
                "read_fct_module": "read_fct_module",
                "write_fct_name": "write_fct_name",
                "write_fct_module": "write_fct_module",
                "job_ids": [],
                "version": "latest",
                "cacheable": False,
                "validity_days": 1,
                "validity_seconds": 1,
                "edition_in_progress": False,
                "data_node_properties": {},
            }
        )
        assert model.edit_in_progress is False
        assert model.last_edit_date == "2020-01-01T00:00:00"
        assert model.owner_id == "owner_id"

    def test_override_deprecated_properties(self):
        model = _DataNodeModel.from_dict(
            {
                "id": "id",
                "config_id": "config_id",
                "scope": repr(Scope.PIPELINE),
                "storage_type": "pickle",
                "name": "name",
                "parent_id": "parent_id",
                "owner_id": "owner_id",
                "parent_ids": ["parent_id"],
                "last_edit_date": "2020-01-02T00:00:00",
                "last_edition_date": "2020-01-01T00:00:00",
                "read_fct_name": "read_fct_name",
                "read_fct_module": "read_fct_module",
                "write_fct_name": "write_fct_name",
                "write_fct_module": "write_fct_module",
                "job_ids": [],
                "version": "latest",
                "cacheable": False,
                "validity_days": 1,
                "validity_seconds": 1,
                "edit_in_progress": True,
                "edition_in_progress": False,
                "data_node_properties": {},
            }
        )
        assert model.edit_in_progress is True
        assert model.last_edit_date == "2020-01-02T00:00:00"
        assert model.owner_id == "owner_id"
