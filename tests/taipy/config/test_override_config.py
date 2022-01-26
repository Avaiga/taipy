from taipy.config.config import Config
from tests.taipy.config.named_temporary_file import NamedTemporaryFile


def test_override_default_configuration_with_code_configuration():
    assert Config.job_config().nb_of_workers == 1
    assert not Config.global_config().notification
    assert len(Config.data_nodes()) == 1
    assert len(Config.tasks()) == 1
    assert len(Config.pipelines()) == 1
    assert len(Config.scenarios()) == 1

    Config.set_job_config(nb_of_workers=-1)
    Config.set_global_config(notification=True)
    foo_config = Config.add_data_node("foo", "in_memory")
    bar_config = Config.add_task("bar", [foo_config], print, [])
    baz_config = Config.add_pipeline("baz", [bar_config])
    qux_config = Config.add_scenario("qux", [baz_config])

    assert Config.job_config().nb_of_workers == -1
    assert Config.global_config().notification
    assert len(Config.data_nodes()) == 2
    assert "default" in Config.data_nodes()
    assert foo_config.name in Config.data_nodes()
    assert Config.data_nodes()[foo_config.name].storage_type == "in_memory"
    assert len(Config.tasks()) == 2
    assert "default" in Config.tasks()
    assert bar_config.name in Config.tasks()
    assert len(Config.tasks()[bar_config.name].inputs) == 1
    assert Config.tasks()[bar_config.name].inputs[0].name == foo_config.name
    assert len(Config.tasks()[bar_config.name].outputs) == 0
    assert Config.tasks()[bar_config.name].function == print
    assert len(Config.pipelines()) == 2
    assert "default" in Config.pipelines()
    assert baz_config.name in Config.pipelines()
    assert len(Config.pipelines()[baz_config.name].tasks) == 1
    assert Config.pipelines()[baz_config.name].tasks[0].name == bar_config.name
    assert len(Config.scenarios()) == 2
    assert "default" in Config.scenarios()
    assert qux_config.name in Config.scenarios()
    assert len(Config.scenarios()[qux_config.name].pipelines) == 1
    assert Config.scenarios()[qux_config.name].pipelines[0].name == baz_config.name


def test_override_default_configuration_with_file_configuration():
    tf = NamedTemporaryFile(
        """
[TAIPY]
notification = true

[JOB]
nb_of_workers = -1

[DATA_NODE.foo]

[TASK.bar]

[PIPELINE.baz]

[SCENARIO.qux]
"""
    )

    assert Config.job_config().nb_of_workers == 1
    assert not Config.global_config().notification
    assert len(Config.data_nodes()) == 1
    assert len(Config.tasks()) == 1
    assert len(Config.pipelines()) == 1
    assert len(Config.scenarios()) == 1

    Config.load(tf.filename)

    assert Config.job_config().nb_of_workers == -1
    assert Config.global_config().notification
    assert len(Config.data_nodes()) == 2
    assert "default" in Config.data_nodes()
    assert "foo" in Config.data_nodes()
    assert len(Config.tasks()) == 2
    assert "default" in Config.tasks()
    assert "bar" in Config.tasks()
    assert len(Config.pipelines()) == 2
    assert "default" in Config.pipelines()
    assert "default" in Config.scenarios()
    assert len(Config.scenarios()) == 2
    assert "baz" in Config.pipelines()
    assert "qux" in Config.scenarios()


def test_code_configuration_do_not_override_file_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config.load(config_from_filename.filename)

    Config.set_job_config(nb_of_workers=21)

    assert Config.job_config().nb_of_workers == 2  # From file config


def test_code_configuration_file_configuration_override_code_configuration():
    config_from_filename = NamedTemporaryFile(
        """
[JOB]
nb_of_workers = 2
    """
    )
    Config.set_job_config(nb_of_workers=21)
    Config.load(config_from_filename.filename)

    assert Config.job_config().nb_of_workers == 2  # From file config


def test_override_default_configuration_with_multiple_configurations():
    file_config = NamedTemporaryFile(
        """
[DATA_NODE.default]
has_header = true
[DATA_NODE.my_datanode]
path = "/data/csv"

[JOB]
nb_of_workers = 10

[TAIPY]
notification = false
    """
    )

    # Default config is applied
    assert Config.job_config().nb_of_workers == 1
    assert Config.global_config().notification is False

    # Code config is applied
    Config.set_job_config(nb_of_workers=-1)
    Config.set_global_config(notification=True)
    assert Config.global_config().notification is True
    assert Config.job_config().nb_of_workers == -1

    # File config is applied
    Config.load(file_config.filename)
    assert Config.global_config().notification is False
    assert Config.job_config().nb_of_workers == 10
    assert Config.data_nodes()["my_datanode"].has_header
    assert Config.data_nodes()["my_datanode"].path == "/data/csv"
    assert Config.data_nodes()["my_datanode"].not_defined is None
