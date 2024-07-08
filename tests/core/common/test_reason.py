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

from taipy.core.reason import Reasons


def test_create_reason():
    reasons = Reasons("entity_id")
    assert reasons.entity_id == "entity_id"
    assert reasons._reasons == {}
    assert reasons
    assert not reasons._entity_id_exists_in_reason("entity_id")
    assert reasons.reasons == ""


def test_add_and_remove_reason():
    reasons = Reasons("entity_id")
    reasons._add_reason("entity_id_1", "Some reason")
    assert reasons._reasons == {"entity_id_1": {"Some reason"}}
    assert not reasons
    assert reasons._entity_id_exists_in_reason("entity_id_1")
    assert reasons.reasons == "Some reason."

    reasons._add_reason("entity_id_1", "Another reason")
    reasons._add_reason("entity_id_2", "Some more reason")
    assert reasons._reasons == {"entity_id_1": {"Some reason", "Another reason"}, "entity_id_2": {"Some more reason"}}
    assert not reasons
    assert reasons._entity_id_exists_in_reason("entity_id_1")
    assert reasons._entity_id_exists_in_reason("entity_id_2")

    reasons._remove_reason("entity_id_1", "Some reason")
    assert reasons._reasons == {"entity_id_1": {"Another reason"}, "entity_id_2": {"Some more reason"}}
    assert not reasons
    assert reasons._entity_id_exists_in_reason("entity_id_1")
    assert reasons._entity_id_exists_in_reason("entity_id_2")

    reasons._remove_reason("entity_id_2", "Some more reason")
    assert reasons._reasons == {"entity_id_1": {"Another reason"}}
    assert not reasons
    assert reasons._entity_id_exists_in_reason("entity_id_1")
    assert not reasons._entity_id_exists_in_reason("entity_id_2")

    reasons._remove_reason("entity_id_1", "Another reason")
    assert reasons._reasons == {}
    assert reasons
    assert not reasons._entity_id_exists_in_reason("entity_id_1")


def test_get_reason_string_from_reason():
    reasons = Reasons("entity_id")
    reasons._add_reason("entity_id_1", "Some reason")
    assert reasons.reasons == "Some reason."

    reasons._add_reason("entity_id_2", "Some more reason")
    assert reasons.reasons == "Some reason; Some more reason."

    reasons._add_reason("entity_id_1", "Another reason")
    assert reasons.reasons.count(";") == 2
    assert "Some reason" in reasons.reasons
    assert "Another reason" in reasons.reasons
    assert "Some more reason" in reasons.reasons
