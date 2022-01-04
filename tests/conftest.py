import os
import shutil

import pytest
from dotenv import load_dotenv

from taipy_rest.app import create_app


@pytest.fixture(scope="session")
def app():
    load_dotenv(".testenv")
    app = create_app(testing=True)
    return app


@pytest.fixture
def datasource_data():
    return {
        "name": "foo",
        "storage_type": "in_memory",
        "scope": "pipeline",
        "default_data": ["1991-01-01T00:00:00"],
    }


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")
