from unittest import mock

from flask import url_for


def test_get_cycle(client, default_cycle):
    # test 404
    user_url = url_for("api.cycle_by_id", cycle_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._get") as manager_mock:
        manager_mock.return_value = default_cycle

        # test get_cycle
        rep = client.get(url_for("api.cycle_by_id", cycle_id="foo"))
        assert rep.status_code == 200


def test_delete_cycle(client):
    # test 404
    user_url = url_for("api.cycle_by_id", cycle_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.cycle._cycle_manager._CycleManager._delete"):
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
