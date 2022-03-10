from importlib import util
from typing import Any, Dict, Optional, Union

from taipy.core.common._utils import _load_fct
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl
from taipy.core.exceptions.exceptions import DependencyNotInstalled


class JobConfig:
    """
    Holds configuration fields related to the job executions.

    Parameters:
        mode (str): The Taipy operating mode. By default, the "standalone" mode is set. On Taipy enterprise,
            the "airflow" mode is available.
        nb_of_workers (int): The maximum number of running workers to execute jobs. It must be a positive integer.
            The default value is 1.
        **properties (dict[str, Any]): A dictionary of additional properties.
    """

    _MODE_KEY = "mode"
    _DEFAULT_MODE = "standalone"

    _NB_OF_WORKERS_KEY = "nb_of_workers"
    _DEFAULT_NB_OF_WORKERS = 1

    def __init__(self, mode: str = None, nb_of_workers: Union[int, str] = None, **properties):
        self.mode = mode

        self.nb_of_workers = nb_of_workers

        self.config = None
        if self.mode and self.mode != self._DEFAULT_MODE:
            self.config = self._external_config(mode, **properties)

        self.properties = properties

    def __getattr__(self, item: str) -> Optional[Any]:
        if self.config:
            if r := getattr(self.config, item, None):
                return r
        return self.properties.get(item)

    @classmethod
    def default_config(cls):
        return JobConfig(cls._DEFAULT_MODE, cls._DEFAULT_NB_OF_WORKERS)

    def _to_dict(self):
        as_dict = {}
        if self.mode is not None:
            as_dict[self._MODE_KEY] = self.mode
        if self.nb_of_workers is not None:
            as_dict[self._NB_OF_WORKERS_KEY] = self.nb_of_workers
        if self.config:
            as_dict.update(self.config._to_dict())
        as_dict.update(self.properties)
        return as_dict

    @classmethod
    def _from_dict(cls, config_as_dict: Dict[str, Any]):
        mode = config_as_dict.pop(cls._MODE_KEY, None)
        nb_of_workers = config_as_dict.pop(cls._NB_OF_WORKERS_KEY, None)
        config = JobConfig(mode, nb_of_workers, **config_as_dict)
        return config

    def _update(self, cfg_as_dict):
        mode = _tpl._replace_templates(cfg_as_dict.pop(self._MODE_KEY, self.mode))
        self.nb_of_workers = _tpl._replace_templates(cfg_as_dict.pop(self._NB_OF_WORKERS_KEY, self.nb_of_workers), int)

        if self.mode != mode:
            self.mode = mode
            self.config = self._external_config(mode, **cfg_as_dict)
            self.config._update(cfg_as_dict)
        elif self.config:
            self.config._update(cfg_as_dict)

        self.properties.update(cfg_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = _tpl._replace_templates(v)

    @property
    def is_standalone(self) -> bool:
        """True if the config is set to standalone execution"""
        return self.mode == self._DEFAULT_MODE

    @property
    def is_multiprocess(self) -> bool:
        """True if the config is set to standalone execution and nb_of_workers is greater than 1"""
        return self.is_standalone and int(self.nb_of_workers) > 1  # type: ignore

    @staticmethod
    def _external_config(mode, **properties):
        dep = f"taipy.{mode}"
        if not util.find_spec(dep):
            raise DependencyNotInstalled(mode)
        return _load_fct(dep + ".config", "Config")(**properties)

    def _is_default_mode(self) -> bool:
        return self.mode == self._DEFAULT_MODE
