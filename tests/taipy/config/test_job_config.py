import pytest

from taipy.config._config import _Config
from taipy.config.config import Config


@pytest.fixture(scope="function", autouse=True)
def reset_configuration_singleton():
    yield
    Config._python_config = _Config()
    Config._file_config = _Config()
    Config._env_config = _Config()
    Config._applied_config = _Config.default_config()


def test_job_config():
    assert Config.job_config().mode == "standalone"
    assert Config.job_config().nb_of_workers == 1
    assert Config.job_config().hostname == "localhost"
    assert Config.job_config().airflow_dags_folder == ".dags/"
    assert Config.job_config().airflow_folder == ".airflow/"
    assert Config.job_config().airflow_db_endpoint is None
    assert Config.job_config().start_airflow is False
    assert Config.job_config().airflow_api_retry == 10

    Config.set_job_config(
        mode=Config.job_config().MODE_VALUE_AIRFLOW,
        hostname="http://localhost:8080",
        nb_of_workers=2,
        airflow_dags_folder=".testDags/",
        airflow_folder=".testAirflow/",
        airflow_db_endpoint=Config.job_config().AIRFLOW_DB_ENDPOINT_KEY,
        start_airflow=True,
    )

    assert Config.job_config().mode == "airflow"
    assert Config.job_config().nb_of_workers == 2
    assert Config.job_config().hostname == "http://localhost:8080"
    assert Config.job_config().airflow_dags_folder == ".testDags/"
    assert Config.job_config().airflow_folder == ".testAirflow/"
    assert Config.job_config().start_airflow is True
    assert Config.job_config().airflow_db_endpoint == "airflow_db_endpoint"
    assert Config.job_config().airflow_api_retry == 10
