# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from taipy.core.reason import ReasonCollection


def test_create_reason():
    reason_collection = ReasonCollection()
    assert reason_collection._reasons == {}
    assert reason_collection
    assert not reason_collection._entity_id_exists_in_reason("entity_id")
    assert reason_collection.reasons == ""


def test_add_and_remove_reason():
    reason_collection = ReasonCollection()
    reason_collection._add_reason("entity_id_1", "Some reason")
    assert reason_collection._reasons == {"entity_id_1": {"Some reason"}}
    assert not reason_collection
    assert reason_collection._entity_id_exists_in_reason("entity_id_1")
    assert reason_collection.reasons == "Some reason."

    reason_collection._add_reason("entity_id_1", "Another reason")
    reason_collection._add_reason("entity_id_2", "Some more reason")
    assert reason_collection._reasons == {
        "entity_id_1": {"Some reason", "Another reason"},
        "entity_id_2": {"Some more reason"},
    }
    assert not reason_collection
    assert reason_collection._entity_id_exists_in_reason("entity_id_1")
    assert reason_collection._entity_id_exists_in_reason("entity_id_2")

    reason_collection._remove_reason("entity_id_1", "Some reason")
    assert reason_collection._reasons == {"entity_id_1": {"Another reason"}, "entity_id_2": {"Some more reason"}}
    assert not reason_collection
    assert reason_collection._entity_id_exists_in_reason("entity_id_1")
    assert reason_collection._entity_id_exists_in_reason("entity_id_2")

    reason_collection._remove_reason("entity_id_2", "Some more reason")
    assert reason_collection._reasons == {"entity_id_1": {"Another reason"}}
    assert not reason_collection
    assert reason_collection._entity_id_exists_in_reason("entity_id_1")
    assert not reason_collection._entity_id_exists_in_reason("entity_id_2")

    reason_collection._remove_reason("entity_id_1", "Another reason")
    assert reason_collection._reasons == {}
    assert reason_collection
    assert not reason_collection._entity_id_exists_in_reason("entity_id_1")


def test_get_reason_string_from_reason():
    reason_collection = ReasonCollection()
    reason_collection._add_reason("entity_id_1", "Some reason")
    assert reason_collection.reasons == "Some reason."

    reason_collection._add_reason("entity_id_2", "Some more reason")
    assert reason_collection.reasons == "Some reason; Some more reason."

    reason_collection._add_reason("entity_id_1", "Another reason")
    assert reason_collection.reasons.count(";") == 2
    assert "Some reason" in reason_collection.reasons
    assert "Another reason" in reason_collection.reasons
    assert "Some more reason" in reason_collection.reasons
