from unittest import mock

import pytest
from flask import url_for


def test_get_cycle(client, default_cycle):
    # test 404
    user_url = url_for("api.cycle_by_id", cycle_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.cycle.manager.cycle_manager.CycleManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_cycle

        # test get_cycle
        rep = client.get(url_for("api.cycle_by_id", cycle_id="foo"))
        assert rep.status_code == 200


def test_delete_cycle(client):
    # test 404
    user_url = url_for("api.cycle_by_id", cycle_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.cycle.manager.cycle_manager.CycleManager.delete"):
        # test get_cycle
        rep = client.delete(url_for("api.cycle_by_id", cycle_id="foo"))
        assert rep.status_code == 200


def test_create_cycle(client, default_cycle_config):
    # without config param
    cycles_url = url_for("api.cycles")
    rep = client.post(cycles_url)
    assert rep.status_code == 400

    # config does not exist
    cycles_url = url_for("api.cycles", config_name="foo")
    rep = client.post(cycles_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy_rest.api.resources.cycle.CycleList.fetch_config"
    ) as config_mock:
        config_mock.return_value = default_cycle_config
        cycles_url = url_for("api.cycles", config_name="bar")
        rep = client.post(cycles_url)
        assert rep.status_code == 201


def test_get_all_cycles(client, default_pipeline, default_cycle_config_list):
    for ds in range(10):
        with mock.patch(
            "taipy_rest.api.resources.cycle.CycleList.fetch_config"
        ) as config_mock:
            config_mock.return_value = default_cycle_config_list[ds]
            cycles_url = url_for("api.cycles", config_name=config_mock.name)
            client.post(cycles_url)

    rep = client.get(cycles_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10


@pytest.mark.xfail()
def test_execute_cycle(client, default_cycle):
    # test 404
    user_url = url_for("api.cycle_submit", cycle_id="foo")
    rep = client.post(user_url)
    assert rep.status_code == 404

    with mock.patch(
        "taipy.cycle.manager.cycle_manager.CycleManager.get"
    ) as manager_mock:
        manager_mock.return_value = default_cycle

        # test get_cycle
        rep = client.post(url_for("api.cycle_submit", cycle_id="foo"))
        assert rep.status_code == 200
