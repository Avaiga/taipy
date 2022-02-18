import os

from taipy.core.config.config import Config
from tests.core.config.named_temporary_file import NamedTemporaryFile


def test_load_from_environment_overwrite_load_from_filename():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
parallel_execution = true
nb_of_workers = 10
    """
    )
    config_from_environment = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 21
    """
    )

    os.environ[Config.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH] = config_from_environment.filename
    Config.load(config_from_filename.filename)

    assert Config.job_config().parallel_execution is True
    assert Config.job_config().nb_of_workers == 21
    os.environ.pop(Config.ENVIRONMENT_VARIABLE_NAME_WITH_CONFIG_PATH)
