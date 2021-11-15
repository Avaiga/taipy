from taipy.config import Config
from tests.taipy.config.named_temporary_file import NamedTemporaryFile


def test_run_in_synchronous():
    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "local"
nb_of_workers = 0
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers == 1

    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "local"
nb_of_workers = 1
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers == 1


def test_run_in_parallel():
    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "local"
nb_of_workers = 2
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers == 2

    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "local"
nb_of_workers = -1
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers is None


def test_run_in_remote():
    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "remote"
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is True
    assert task_scheduler_configs.hostname == "localhost"
    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers is None

    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "remote"
nb_of_workers = 42
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is True
    assert task_scheduler_configs.hostname == "localhost"
    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers == 42


def test_nb_of_workers_negative_boundary():
    tf = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = -42
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers == 42

    tf = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = 5.3
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers == 5


def test_execution_env_is_not_necessary_locally():
    tf = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = 2
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is True
    assert task_scheduler_configs.nb_of_workers == 2

    tf = NamedTemporaryFile(
        """
[TASK]
nb_of_workers = 1
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.parallel_execution is False
    assert task_scheduler_configs.nb_of_workers == 1


def test_remote_with_hostname():
    tf = NamedTemporaryFile(
        """
[TASK]
execution_env = "remote"
hostname = "foo"
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is True
    assert task_scheduler_configs.hostname == "foo"

    export = NamedTemporaryFile()

    export_expected = """
[TASK]
execution_env = "remote"
nb_of_workers = -1
hostname = "foo"

[DATA_SOURCE.default]
"""

    Config.export(export.filename)
    assert export.read().strip() == export_expected.strip()


def test_hostname_not_set_if_not_remote():
    tf = NamedTemporaryFile(
        """
[TASK]
hostname = "localhost"
"""
    )

    Config.load(tf.filename)

    task_scheduler_configs = Config.task_scheduler_configs.create()

    assert task_scheduler_configs.remote_execution is False
    assert task_scheduler_configs.hostname is None
