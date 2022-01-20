from unittest import mock

from flask import url_for
from taipy.config import DataSourceConfig
from taipy.data import Scope


def test_get_datasource(client):
    # test 404
    user_url = url_for("api.datasource_by_id", datasource_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    data = {
        "config_name": "foo",
        "validity_minutes": None,
        "edition_in_progress": False,
        "scope": "Scope.PIPELINE",
        "job_ids": [],
        "validity_days": None,
        "parent_id": None,
        "name": "DATASOURCE_foo_09d756d4-e2f1-42c9-a9b4-2cef9f293462",
        "properties": {"default_data": ["1991-01-01T00:00:00"]},
        "validity_hours": None,
        "id": "foo",
        "last_edition_date": "2021-12-28 21:17:54.652829",
    }

    with mock.patch("taipy.data.manager.data_manager.DataManager.get") as manager_mock:
        manager_mock.return_value = data

        # test get_datasource
        rep = client.get(url_for("api.datasource_by_id", datasource_id="foo"))
        assert rep.status_code == 200


def test_delete_datasource(client):
    # test 404
    user_url = url_for("api.datasource_by_id", datasource_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.data.manager.data_manager.DataManager.delete"):
        # test get_datasource
        rep = client.delete(url_for("api.datasource_by_id", datasource_id="foo"))
        assert rep.status_code == 200


def test_create_datasource(client, default_datasource_config):
    # without config param
    datasources_url = url_for("api.datasources")
    rep = client.post(datasources_url)
    assert rep.status_code == 400

    # config does not exist
    datasources_url = url_for("api.datasources", config_name="foo")
    rep = client.post(datasources_url)
    assert rep.status_code == 404

    with mock.patch("taipy_rest.api.resources.datasource.DataSourceList.fetch_config") as config_mock:
        config_mock.return_value = default_datasource_config
        datasources_url = url_for("api.datasources", config_name="bar")
        rep = client.post(datasources_url)
        assert rep.status_code == 201


def test_get_all_datasources(client, default_datasource_config_list):
    for ds in range(10):
        with mock.patch("taipy_rest.api.resources.datasource.DataSourceList.fetch_config") as config_mock:
            config_mock.return_value = default_datasource_config_list[ds]
            datasources_url = url_for("api.datasources", config_name=config_mock.name)
            client.post(datasources_url)

    rep = client.get(datasources_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10
