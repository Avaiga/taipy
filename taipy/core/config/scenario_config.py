from collections import defaultdict
from copy import copy
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.core.common._validate_id import _validate_id
from taipy.core.common.frequency import Frequency
from taipy.core.config._config_template_handler import _ConfigTemplateHandler as _tpl
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.exceptions.exceptions import NonExistingComparator


class ScenarioConfig:
    """
    Holds all the configuration fields needed to instantiate an actual `Scenario^` from the `ScenarioConfig`.

    Attributes:
        id (str): Identifier of the scenario config. It must be a valid Python variable name.
        pipeline_configs (`PipelineConfig^` or List[`PipelineConfig^`]): List of pipeline configs. The default value
            is [].
        **properties: A dictionary of additional properties.
    """

    _PIPELINE_KEY = "pipelines"
    _FREQUENCY_KEY = "frequency"
    _COMPARATOR_KEY = "comparators"

    def __init__(
        self,
        id: str,
        pipelines: Union[PipelineConfig, List[PipelineConfig]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        self.id = _validate_id(id)
        self.properties = properties
        if pipelines:
            self._pipelines = [pipelines] if isinstance(pipelines, PipelineConfig) else copy(pipelines)
        else:
            self._pipelines = []
        self.frequency = frequency
        self.comparators = defaultdict(list)
        if comparators:
            for k, v in comparators.items():
                if isinstance(v, list):
                    self.comparators[_validate_id(k)].extend(v)
                else:
                    self.comparators[_validate_id(k)].append(v)

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        comp = None if self.comparators is None else self.comparators
        return ScenarioConfig(self.id, copy(self._pipelines), self.frequency, copy(comp), **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return ScenarioConfig(id, [], None, dict())

    @property
    def pipeline_configs(self) -> List[PipelineConfig]:
        return self._pipelines

    def _to_dict(self):
        return {self._PIPELINE_KEY: self._pipelines, self._FREQUENCY_KEY: self.frequency, **self.properties}

    @classmethod
    def _from_dict(cls, id: str, config_as_dict: Dict[str, Any], pipeline_configs: Dict[str, PipelineConfig]):
        config = ScenarioConfig(id)
        config.id = _validate_id(id)
        if pipeline_ids := config_as_dict.pop(cls._PIPELINE_KEY, None):
            config._pipelines = [pipeline_configs[p_id] for p_id in pipeline_ids if p_id in pipeline_configs]
        config.frequency = config_as_dict.pop(cls._FREQUENCY_KEY, None)
        config.comparators = config_as_dict.pop(cls._COMPARATOR_KEY, dict())
        config.properties = config_as_dict
        return config

    def _update(self, config_as_dict, default_scenario_cfg=None):
        self._pipelines = (
            config_as_dict.pop(self._PIPELINE_KEY, self._pipelines)
            if config_as_dict.pop(self._PIPELINE_KEY, self._pipelines) is not None
            else default_scenario_cfg._pipelines
        )
        if self._pipelines is None and default_scenario_cfg:
            self._pipelines = default_scenario_cfg._pipelines
        self.frequency = config_as_dict.pop(self._FREQUENCY_KEY, self.frequency) or default_scenario_cfg.frequency
        self.comparators = config_as_dict.pop(self._COMPARATOR_KEY, self.comparators)
        if self.comparators is None and default_scenario_cfg:
            self.comparators = default_scenario_cfg.comparators
        self.properties.update(config_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = _tpl._replace_templates(v)

    def add_comparator(self, dn_config_id: str, comparator: Callable):
        self.comparators[dn_config_id].append(comparator)

    def delete_comparator(self, dn_config_id: str):
        if dn_config_id in self.comparators:
            del self.comparators[dn_config_id]
        else:
            raise NonExistingComparator
