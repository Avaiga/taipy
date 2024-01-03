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

import json
import os
from datetime import datetime, timedelta

import pytest
from taipy.core._repository._decoder import _Decoder
from taipy.core._repository._encoder import _Encoder


@pytest.fixture(scope="function", autouse=True)
def create_and_delete_json_file():
    test_json_file = {
        "name": "testing",
        "date": datetime(1991, 1, 1),
        "default_data": "data for testing encoder",
        "validity_period": timedelta(days=1),
    }
    with open("data.json", "w") as f:
        json.dump(test_json_file, f, ensure_ascii=False, indent=4, cls=_Encoder)
    yield
    os.unlink("data.json")


def test_json_encoder():
    with open("data.json") as json_file:
        data = json.load(json_file)
        assert data["name"] == "testing"
        assert data["default_data"] == "data for testing encoder"
        assert data["date"] == {
            "__type__": "Datetime",
            "__value__": "1991-01-01T00:00:00",
        }
        assert data["date"].get("__type__") == "Datetime"
        assert data["date"].get("__value__") == "1991-01-01T00:00:00"


def test_json_decoder():
    with open("data.json") as json_file:
        data = json.load(json_file, cls=_Decoder)
        assert data["name"] == "testing"
        assert data["default_data"] == "data for testing encoder"
        assert data["date"] == datetime(1991, 1, 1)
