# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""# Taipy Config

The Taipy Config package is a Python library designed to configure a Taipy application.

The main entrypoint is the `Config^` singleton class. It exposes some methods to configure the
Taipy application and some attributes to retrieve the configuration values.

"""

from typing import List

from ._init import Config
from .checker.issue import Issue
from .checker.issue_collector import IssueCollector
from .common.frequency import Frequency
from .common.scope import Scope
from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection
from .version import _get_version

__version__ = _get_version()


def _config_doc(func):
    def func_with_doc(section, attribute_name, default, configuration_methods, add_to_unconflicted_sections=False):
        import os

        if os.environ.get("GENERATING_TAIPY_DOC", None) and os.environ["GENERATING_TAIPY_DOC"] == "true":
            with open("config_doc.txt", "a") as f:
                from inspect import signature

                for exposed_configuration_method, configuration_method in configuration_methods:
                    annotation = "    @staticmethod\n"
                    sign = "    def " + exposed_configuration_method + str(signature(configuration_method)) + ":\n"
                    doc = '        """' + configuration_method.__doc__ + '"""\n'
                    content = "        pass\n\n"
                    f.write(annotation + sign + doc + content)
        return func(section, attribute_name, default, configuration_methods, add_to_unconflicted_sections)

    return func_with_doc


@_config_doc
def _inject_section(
    section_clazz,
    attribute_name: str,
    default: Section,
    configuration_methods: List[tuple],
    add_to_unconflicted_sections: bool = False,
):
    Config._register_default(default)

    if issubclass(section_clazz, UniqueSection):
        setattr(Config, attribute_name, Config.unique_sections[section_clazz.name])
    elif issubclass(section_clazz, Section):
        setattr(Config, attribute_name, Config.sections[section_clazz.name])
    else:
        raise TypeError

    if add_to_unconflicted_sections:
        Config._comparator._add_unconflicted_section(section_clazz.name)  # type: ignore[attr-defined]

    for exposed_configuration_method, configuration_method in configuration_methods:
        setattr(Config, exposed_configuration_method, configuration_method)
