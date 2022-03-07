from collections import defaultdict
from copy import copy
from typing import Any, Callable, Dict, List, Optional, Union

from taipy.core.common._unicode_to_python_variable_name import _protect_name
from taipy.core.common.frequency import Frequency
from taipy.core.config.config_template_handler import ConfigTemplateHandler as tpl
from taipy.core.config.pipeline_config import PipelineConfig
from taipy.core.exceptions.scenario import NonExistingComparator


class ScenarioConfig:
    """
    Holds all the configuration fields needed to create actual scenarios from the ScenarioConfig.

    Attributes:
        id (str): Identifier of the scenario config.
            We strongly recommend to use lowercase alphanumeric characters, dash character '-', or underscore character
            '_'. Note that other characters are replaced according the following rules :
            - Space characters are replaced by underscore characters ('_').
            - Unicode characters are replaced by a corresponding alphanumeric character using the Unicode library.
            - Other characters are replaced by dash characters ('-').
        pipelines (list): List of pipeline configs. Default value: [].
        properties (dict): Dictionary of additional properties.
    """

    PIPELINE_KEY = "pipelines"
    FREQUENCY_KEY = "frequency"
    COMPARATOR_KEY = "comparators"

    def __init__(
        self,
        id: str,
        pipelines: Union[PipelineConfig, List[PipelineConfig]] = None,
        frequency: Optional[Frequency] = None,
        comparators: Optional[Dict[str, Union[List[Callable], Callable]]] = None,
        **properties,
    ):
        self.id = _protect_name(id)
        self.properties = properties
        if pipelines:
            self.pipelines = [pipelines] if isinstance(pipelines, PipelineConfig) else copy(pipelines)
        else:
            self.pipelines = []
        self.frequency = frequency
        self.comparators = defaultdict(list)
        if comparators:
            for k, v in comparators.items():
                if isinstance(v, list):
                    self.comparators[_protect_name(k)].extend(v)
                else:
                    self.comparators[_protect_name(k)].append(v)

    def __getattr__(self, item: str) -> Optional[Any]:
        return self.properties.get(item)

    def __copy__(self):
        comp = None if self.comparators is None else self.comparators
        return ScenarioConfig(self.id, copy(self.pipelines), self.frequency, copy(comp), **copy(self.properties))

    @classmethod
    def default_config(cls, id):
        return ScenarioConfig(id, [], None, dict())

    @property
    def pipelines_configs(self) -> List[PipelineConfig]:
        return self.pipelines

    def to_dict(self):
        return {self.PIPELINE_KEY: self.pipelines, self.FREQUENCY_KEY: self.frequency, **self.properties}

    @classmethod
    def from_dict(cls, id: str, config_as_dict: Dict[str, Any], pipeline_configs: Dict[str, PipelineConfig]):
        config = ScenarioConfig(id)
        config.id = _protect_name(id)
        if pipeline_ids := config_as_dict.pop(cls.PIPELINE_KEY, None):
            config.pipelines = [pipeline_configs[p_id] for p_id in pipeline_ids if p_id in pipeline_configs]
        config.frequency = config_as_dict.pop(cls.FREQUENCY_KEY, None)
        config.comparators = config_as_dict.pop(cls.COMPARATOR_KEY, dict())
        config.properties = config_as_dict
        return config

    def update(self, config_as_dict, default_scenario_cfg=None):
        self.pipelines = config_as_dict.pop(self.PIPELINE_KEY, self.pipelines)
        if self.pipelines is None and default_scenario_cfg:
            self.pipelines = default_scenario_cfg.pipelines
        self.frequency = config_as_dict.pop(self.FREQUENCY_KEY, self.frequency) or default_scenario_cfg.frequency
        self.comparators = config_as_dict.pop(self.COMPARATOR_KEY, self.comparators)
        if self.comparators is None and default_scenario_cfg:
            self.comparators = default_scenario_cfg.comparators
        self.properties.update(config_as_dict)
        for k, v in self.properties.items():
            self.properties[k] = tpl.replace_templates(v)

    def add_comparator(self, dn_config_id: str, comparator: Callable):
        self.comparators[dn_config_id].append(comparator)

    def delete_comparator(self, dn_config_id: str):
        if dn_config_id in self.comparators:
            del self.comparators[dn_config_id]
        else:
            raise NonExistingComparator
