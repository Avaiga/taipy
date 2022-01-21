from taipy.common import protect_name
from taipy.config import DataSourceConfig, GlobalAppConfig, JobConfig, PipelineConfig, ScenarioConfig, TaskConfig
from taipy.config._config import _Config
from taipy.config.config import Config
from taipy.data import Scope


def _test_default_global_app_config(global_config: GlobalAppConfig):
    assert global_config is not None
    assert not global_config.notification
    assert global_config.root_folder == "./taipy/"
    assert global_config.storage_folder == ".data/"
    assert global_config.broker_endpoint is None
    assert len(global_config.properties) == 0


def _test_default_job_config(job_config: JobConfig):
    assert job_config is not None
    assert job_config.mode == "standalone"
    assert job_config.nb_of_workers == 1
    assert job_config.hostname == "localhost"
    assert job_config.airflow_folder == ".airflow/"
    assert job_config.airflow_dags_folder == ".dags/"
    assert job_config.airflow_db_endpoint is None
    assert len(job_config.properties) == 0


def _test_default_data_source_config(ds_config: DataSourceConfig):
    assert ds_config is not None
    assert ds_config.name is not None
    assert ds_config.name == protect_name(ds_config.name)
    assert ds_config.storage_type == "pickle"
    assert ds_config.scope == Scope.PIPELINE
    assert len(ds_config.properties) == 0


def _test_default_task_config(task_config: TaskConfig):
    assert task_config is not None
    assert task_config.name is not None
    assert task_config.name == protect_name(task_config.name)
    assert task_config.inputs == []
    assert task_config.outputs == []
    assert task_config.function is None
    assert len(task_config.properties) == 0


def _test_default_pipeline_config(pipeline_config: PipelineConfig):
    assert pipeline_config is not None
    assert pipeline_config.name is not None
    assert pipeline_config.name == protect_name(pipeline_config.name)
    assert pipeline_config.tasks == []
    assert len(pipeline_config.properties) == 0


def _test_default_scenario_config(scenario_config: ScenarioConfig):
    assert scenario_config is not None
    assert scenario_config.name is not None
    assert scenario_config.name == protect_name(scenario_config.name)
    assert scenario_config.pipelines == []
    assert len(scenario_config.properties) == 0


def test_default_configuration():
    default_config = _Config.default_config()

    _test_default_global_app_config(default_config.global_config)
    _test_default_global_app_config(Config.global_config())
    _test_default_global_app_config(GlobalAppConfig().default_config())

    _test_default_job_config(default_config.job_config)
    _test_default_job_config(Config.job_config())
    _test_default_job_config(JobConfig().default_config())

    _test_default_data_source_config(default_config.data_sources[_Config.DEFAULT_KEY])
    _test_default_data_source_config(Config.data_sources()[_Config.DEFAULT_KEY])
    _test_default_data_source_config(DataSourceConfig.default_config("DEFAULT_KEY"))
    assert len(default_config.data_sources) == 1
    assert len(Config.data_sources()) == 1

    _test_default_task_config(default_config.tasks[_Config.DEFAULT_KEY])
    _test_default_task_config(Config.tasks()[_Config.DEFAULT_KEY])
    _test_default_task_config(TaskConfig.default_config("DEFAULT_KEY"))
    assert len(default_config.tasks) == 1
    assert len(Config.tasks()) == 1

    _test_default_pipeline_config(default_config.pipelines[_Config.DEFAULT_KEY])
    _test_default_pipeline_config(Config.pipelines()[_Config.DEFAULT_KEY])
    _test_default_pipeline_config(PipelineConfig.default_config("DEFAULT_KEY"))
    assert len(default_config.pipelines) == 1
    assert len(Config.pipelines()) == 1

    _test_default_scenario_config(default_config.scenarios[_Config.DEFAULT_KEY])
    _test_default_scenario_config(Config.scenarios()[_Config.DEFAULT_KEY])
    _test_default_scenario_config(ScenarioConfig.default_config("DEFAULT_KEY"))
    assert len(default_config.scenarios) == 1
    assert len(Config.scenarios()) == 1
