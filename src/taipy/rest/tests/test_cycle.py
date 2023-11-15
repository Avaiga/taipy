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

from unittest import mock

from flask import url_for


def test_get_cycle(client, default_cycle):
    # test 404
    cycle_url = url_for("api.cycle_by_id", cycle_id="foo")
    rep = client.get(cycle_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._get") as manager_mock:
        manager_mock.return_value = default_cycle

        # test get_cycle
        rep = client.get(url_for("api.cycle_by_id", cycle_id="foo"))
        assert rep.status_code == 200


def test_delete_cycle(client):
    # test 404
    cycle_url = url_for("api.cycle_by_id", cycle_id="foo")
    rep = client.get(cycle_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._delete"), mock.patch(
        "taipy.core.cycle._cycle_manager._CycleManager._get"
    ):
        # test get_cycle
        rep = client.delete(url_for("api.cycle_by_id", cycle_id="foo"))
        assert rep.status_code == 200


def test_create_cycle(client, cycle_data):
    # without config param
    cycles_url = url_for("api.cycles")
    data = {"bad": "data"}
    rep = client.post(cycles_url, json=data)
    assert rep.status_code == 400

    rep = client.post(cycles_url, json=cycle_data)
    assert rep.status_code == 201


def test_get_all_cycles(client, create_cycle_list):
    cycles_url = url_for("api.cycles")
    rep = client.get(cycles_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10
