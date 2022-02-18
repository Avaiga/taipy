import os
from importlib import util
from unittest import mock

import pytest

from taipy.core.config._config import _Config
from taipy.core.config.config import Config


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_file_config = _Config()
    Config._applied_config = _Config.default_config()


def test_job_config():
    if not util.find_spec("taipy_airflow"):
        pytest.skip()
    assert Config.job_config().mode == "standalone"
    assert Config.job_config().nb_of_workers == 1

    Config.set_job_config(
        mode=Config.job_config().MODE_VALUE_AIRFLOW,
        hostname="http://localhost:8080",
        nb_of_workers=2,
        airflow_dags_folder=".testDags/",
        airflow_folder=".testAirflow/",
        start_airflow=True,
        airflow_user="taipy",
        airflow_password="password",
    )

    assert Config.job_config().mode == "airflow"
    assert Config.job_config().nb_of_workers == 2
    assert Config.job_config().hostname == "http://localhost:8080"
    assert Config.job_config().airflow_dags_folder == ".testDags/"
    assert Config.job_config().airflow_folder == ".testAirflow/"
    assert Config.job_config().start_airflow is True
    assert Config.job_config().airflow_api_retry == 10
    assert Config.job_config().airflow_user == "taipy"
    assert Config.job_config().airflow_password == "password"

    with mock.patch.dict(os.environ, {"FOO": "36", "BAR": "baz", "USER": "user", "PASS": "pass"}):
        Config.set_job_config(
            mode=Config.job_config().MODE_VALUE_AIRFLOW,
            hostname="http://localhost:8080",
            nb_of_workers="ENV[FOO]",
            airflow_dags_folder=".testDags/",
            airflow_folder=".testAirflow/",
            start_airflow=True,
            airflow_user="ENV[USER]",
            airflow_password="ENV[PASS]",
            prop="ENV[BAR]",
        )
        assert Config.job_config().mode == "airflow"
        assert Config.job_config().nb_of_workers == 36
        assert Config.job_config().hostname == "http://localhost:8080"
        assert Config.job_config().airflow_dags_folder == ".testDags/"
        assert Config.job_config().airflow_folder == ".testAirflow/"
        assert Config.job_config().start_airflow is True
        assert Config.job_config().airflow_api_retry == 10
        assert Config.job_config().airflow_user == "user"
        assert Config.job_config().airflow_password == "pass"
        assert Config.job_config().prop == "baz"
