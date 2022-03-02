from importlib import util
from typing import Any, Dict, Optional, Union

from taipy.core.common.utils import load_fct
from taipy.core.config.config_template_handler import ConfigTemplateHandler as tpl
from taipy.core.exceptions.scheduler import DependencyNotInstalled


class JobConfig:
    """
    Holds configuration fields related to the job executions.

    Parameters:
        mode (str): Field representing the Taipy operating mode. Possible values are "standalone", "airflow". Default
            value: "standalone".
        nb_of_workers (int): Maximum number of running workers to execute jobs. Must be a positive integer.
            Default value : 1
        hostname (str): Hostname. Default value is "http://localhost:8080".
        airflow_dags_folder (str): Folder name used to store the dags to be read by airflow if airflow mode is activated.
            Default value is ".dag/". It is used in conjunction with the GlobalAppConfig.root_folder field. That means
            the path for the airflow dag folder is <root_folder><airflow_dags_folder> (Default path : "./taipy/.dag/").
        airflow_folder (str): Folder name used by airflow if airflow mode is activated. Default value is ".airflow/". It
            is used in conjunction with the GlobalAppConfig.root_folder field. That means the path for the airflow dag
            folder is <root_folder><airflow_dags_folder> (Default path : "./taipy/.airflow/").
        start_airflow (bool): Allow Taipy to start Airflow if not alreay started.
        airflow_api_retry (int): Retry pattern on Airflow APIs.
        airflow_user (str): User name used with the REST API. Default value is "taipy".
        airflow_password (str): Password used with the REST API. Default value is "taipy".
        properties (dict): Dictionary of additional properties.

    """

    MODE_KEY = "mode"
    MODE_VALUE_STANDALONE = "standalone"
    MODE_VALUE_AIRFLOW = "airflow"
    DEFAULT_MODE = MODE_VALUE_STANDALONE

    NB_OF_WORKERS_KEY = "nb_of_workers"
    DEFAULT_NB_OF_WORKERS = 1

    def __init__(self, mode: str = None, nb_of_workers: Union[int, str] = None, **properties):
        self.mode = mode

        self.nb_of_workers = nb_of_workers

        self.config = None
        if self.mode and self.mode != self.DEFAULT_MODE:
            self.config = self._external_config(mode, **properties)

        self.properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        if self.config:
            if r := getattr(self.config, item, None):
                return r
        return self.properties.get(item)

    @classmethod
    def default_config(cls):
        return JobConfig(cls.DEFAULT_MODE, cls.DEFAULT_NB_OF_WORKERS)

    def to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self.MODE_KEY] = self.mode
        if self.nb_of_workers is not None:
            as_dict[self.NB_OF_WORKERS_KEY] = self.nb_of_workers
        if self.config:
            as_dict.update(self.config.to_dict())
        as_dict.update(self.properties)
        return as_dict

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]):
        mode = config_as_dict.pop(cls.MODE_KEY, None)
        nb_of_workers = config_as_dict.pop(cls.NB_OF_WORKERS_KEY, None)
        config = JobConfig(mode, nb_of_workers, **config_as_dict)
        return config

    def update(self, cfg_as_dict):
        mode = tpl.replace_templates(cfg_as_dict.pop(self.MODE_KEY, self.mode))
        self.nb_of_workers = tpl.replace_templates(cfg_as_dict.pop(self.NB_OF_WORKERS_KEY, self.nb_of_workers), int)

        if self.mode != mode:
            self.mode = mode
            self.config = self._external_config(mode, **cfg_as_dict)
            self.config.update(cfg_as_dict)
        elif self.config:
            self.config.update(cfg_as_dict)

        self.properties.update(cfg_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = tpl.replace_templates(v)

    @property
    def is_standalone(self) -> bool:
        """True if the config is set to standalone execution"""
        return self.mode == self.MODE_VALUE_STANDALONE

    @property
    def is_multiprocess(self) -> bool:
        """True if the config is set to standalone execution and nb_of_workers is greater than 1"""
        return self.is_standalone and int(self.nb_of_workers) > 1  # type: ignore

    @staticmethod
    def _external_config(mode, **properties):
        dep = f"taipy.{mode}"
        if not util.find_spec(dep):
            raise DependencyNotInstalled(mode)
        return load_fct(dep + ".config", "Config")(**properties)
