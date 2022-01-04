import os
import shutil

import pytest
from dotenv import load_dotenv
from taipy.common.alias import DataSourceId
from taipy.data import InMemoryDataSource, Scope
from taipy.task import Task

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


@pytest.fixture
def task_data():
    return {
        "config_name": "foo",
        "input_ids": ["DATASOURCE_foo_3b888e17-1974-4a56-a42c-c7c96bc9cd54"],
        "function_name": "print",
        "function_module": "builtins",
        "output_ids": ["DATASOURCE_foo_4d9923b8-eb9f-4f3c-8055-3a1ce8bee309"],
    }


@pytest.fixture
def default_datasource():
    return InMemoryDataSource(
        "input_ds",
        Scope.SCENARIO,
        DataSourceId("id_uio"),
        "my name",
        "parent_id",
        properties={"default_data": "In memory Data Source"},
    )


@pytest.fixture
def default_task():
    input_ds = InMemoryDataSource(
        "input_ds",
        Scope.SCENARIO,
        DataSourceId("id_uio"),
        "my name",
        "parent_id",
        properties={"default_data": "In memory Data Source"},
    )

    output_ds = InMemoryDataSource(
        "output_ds",
        Scope.SCENARIO,
        DataSourceId("id_uio"),
        "my name",
        "parent_id",
        properties={"default_data": "In memory Data Source"},
    )
    return Task(
        "foo",
        [input_ds],
        print,
        [output_ds],
        None,
    )


@pytest.fixture(autouse=True)
def cleanup_files():
    if os.path.exists(".data"):
        shutil.rmtree(".data")
