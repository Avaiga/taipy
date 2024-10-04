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

""" The `taipy.common.config` package provides features to configure a Taipy application.

Its main class is the `Config^` singleton. It exposes various static methods
and attributes to configure the Taipy application and retrieve the configuration values.

!!! example "Standard usage"

    ```python
    from taipy.common.config import Config
    from taipy.common.config import Frequency
    from taipy.common.config import Scope

    data_node_cfg = Config.configure_data_node("my_data_node", scope=Scope.SCENARIO)
    Config.configure_scenario("my_scenario", additional_data_node_configs=[data_node_cfg], frequency=Frequency.DAILY)
    Config.configure_core(repository_type="filesystem", storage_folder="my/storage/folder")
    Config.configure_authentication(protocol="taipy",roles={"user1": ["role1", "TAIPY_READER"]})

    print(Config.data_nodes["my_data_node"].scope)  # Output: SCENARIO
    print(len(Config.scenarios["my_scenario"].data_nodes))  # Output: 1
    ```

    In this example, the static methods of the `Config^` singleton are used to configure
    a Taipy application. The application has one data node configuration and one scenario
    configuration.
    We also configure the application to use a filesystem repository and set up authentication.

!!! note "`Frequency^` and `Scope^` for scenario and data nodes configurations"

    Besides the `Config^` class which is the main entrypoint, the `taipy.common.config` package exposes
    the `Frequency^` and `Scope^` enums that are frequently used to configure data nodes and
    scenarios.

    The three objects are exposed in the `taipy^` package directly for convenience.

"""

from typing import List

from ._init import Config
from .common.frequency import Frequency
from .common.scope import Scope
from .global_app.global_app_config import GlobalAppConfig
from .section import Section
from .unique_section import UniqueSection


def _config_doc(func):
    def func_with_doc(section, attr_name, default, configuration_methods, add_to_unconflicted_sections=False):
        import os

        if os.environ.get("GENERATING_TAIPY_DOC", None) and os.environ["GENERATING_TAIPY_DOC"] == "true":
            with (open("config_doc.txt", "a") as f):
                from inspect import signature

                # Add the documentation for configure methods
                for exposed_configuration_method, configuration_method in configuration_methods:
                    annotation = "    @staticmethod\n"
                    sign = "    def " + exposed_configuration_method + str(signature(configuration_method)) + ":\n"
                    doc = '        """' + configuration_method.__doc__ + '"""\n'
                    content = "        pass\n\n"
                    f.write(annotation + sign + doc + content)

                # Add the documentation for the attribute
                annotation = '    @property\n'
                sign = f"    def {attr_name} (self) -> {section.__name__}:\n"
                if issubclass(section, UniqueSection):
                    doc = f'        """The configured {section.__name__} section."""\n'
                elif issubclass(section, Section):
                    doc = f'        """The configured {section.__name__} sections ."""\n'
                else:
                    print(f" ERROR - Invalid section class: {section.__name__}")  # noqa: T201
                    return
                content = "        pass\n\n"
                f.write(annotation + sign + doc + content)
        return func(section, attr_name, default, configuration_methods, add_to_unconflicted_sections)

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
