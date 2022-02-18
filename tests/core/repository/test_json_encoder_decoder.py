import json
import os
from datetime import datetime

import pytest

from taipy.core.repository.fs_base import CustomDecoder, CustomEncoder


@pytest.fixture(scope="function", autouse=True)
def create_and_delete_json_file():
    test_json_file = {"name": "testing", "date": datetime(1991, 1, 1), "default_data": "data for testing encoder"}
    with open("data.json", "w") as f:
        json.dump(test_json_file, f, ensure_ascii=False, indent=4, cls=CustomEncoder)
    yield
    os.unlink("data.json")


def test_json_encoder():
    with open("data.json") as json_file:
        data = json.load(json_file)
        assert data["name"] == "testing"
        assert data["default_data"] == "data for testing encoder"
        assert data["date"] == {"__type__": "Datetime", "__value__": "1991-01-01T00:00:00"}
        assert data["date"].get("__type__") == "Datetime"
        assert data["date"].get("__value__") == "1991-01-01T00:00:00"


def test_json_decoder():
    with open("data.json") as json_file:
        data = json.load(json_file, cls=CustomDecoder)
        assert data["name"] == "testing"
        assert data["default_data"] == "data for testing encoder"
        assert data["date"] == datetime(1991, 1, 1)
