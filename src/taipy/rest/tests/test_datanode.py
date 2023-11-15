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

import pytest
from flask import url_for


def test_get_datanode(client, default_datanode):
    # test 404
    user_url = url_for("api.datanode_by_id", datanode_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.data._data_manager._DataManager._get") as manager_mock:
        manager_mock.return_value = default_datanode
        # test get_datanode
        rep = client.get(url_for("api.datanode_by_id", datanode_id="foo"))
        assert rep.status_code == 200


def test_delete_datanode(client):
    # test 404
    user_url = url_for("api.datanode_by_id", datanode_id="foo")
    rep = client.get(user_url)
    assert rep.status_code == 404

    with mock.patch("taipy.core.data._data_manager._DataManager._delete"), mock.patch(
        "taipy.core.data._data_manager._DataManager._get"
    ):
        # test get_datanode
        rep = client.delete(url_for("api.datanode_by_id", datanode_id="foo"))
        assert rep.status_code == 200


def test_create_datanode(client, default_datanode_config):
    # without config param
    datanodes_url = url_for("api.datanodes")
    rep = client.post(datanodes_url)
    assert rep.status_code == 400

    # config does not exist
    datanodes_url = url_for("api.datanodes", config_id="foo")
    rep = client.post(datanodes_url)
    assert rep.status_code == 404

    with mock.patch("src.taipy.rest.api.resources.datanode.DataNodeList.fetch_config") as config_mock:
        config_mock.return_value = default_datanode_config
        datanodes_url = url_for("api.datanodes", config_id="bar")
        rep = client.post(datanodes_url)
        assert rep.status_code == 201


def test_get_all_datanodes(client, default_datanode_config_list):
    for ds in range(10):
        with mock.patch("src.taipy.rest.api.resources.datanode.DataNodeList.fetch_config") as config_mock:
            config_mock.return_value = default_datanode_config_list[ds]
            datanodes_url = url_for("api.datanodes", config_id=config_mock.name)
            client.post(datanodes_url)

    rep = client.get(datanodes_url)
    assert rep.status_code == 200

    results = rep.get_json()
    assert len(results) == 10


def test_read_datanode(client, default_df_datanode):
    with mock.patch("taipy.core.data._data_manager._DataManager._get") as config_mock:
        config_mock.return_value = default_df_datanode

        # without operators
        datanodes_url = url_for("api.datanode_reader", datanode_id="foo")
        rep = client.get(datanodes_url, json={})
        assert rep.status_code == 200

        # Without operators and body
        rep = client.get(datanodes_url)
        assert rep.status_code == 200

        # TODO: Revisit filter test
        # operators = {"operators": [{"key": "a", "value": 5, "operator": "LESS_THAN"}]}
        # rep = client.get(datanodes_url, json=operators)
        # assert rep.status_code == 200


def test_write_datanode(client, default_datanode):
    with mock.patch("taipy.core.data._data_manager._DataManager._get") as config_mock:
        config_mock.return_value = default_datanode
        # Get DataNode
        datanodes_read_url = url_for("api.datanode_reader", datanode_id=default_datanode.id)
        rep = client.get(datanodes_read_url, json={})
        assert rep.status_code == 200
        assert rep.json == {"data": [1, 2, 3, 4, 5, 6]}

        datanodes_write_url = url_for("api.datanode_writer", datanode_id=default_datanode.id)
        rep = client.put(datanodes_write_url, json=[1, 2, 3])
        assert rep.status_code == 200

        rep = client.get(datanodes_read_url, json={})
        assert rep.status_code == 200
        assert rep.json == {"data": [1, 2, 3]}
