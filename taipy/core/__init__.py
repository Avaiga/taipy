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

"""
The Taipy `core` package provides powerful, customized, data-driven back-end functionalities.
It provides the tools to help data scientists and Python developers transform their algorithms
into a complete back-end application. In  particular, it helps with:

- Data Integration
- Task Orchestration
- What-if Analysis
- Version management

More details on the Core functionalities are available in the user manual.

To use such functionalities, the first step consists of setting up the Taipy configuration to design
your application's characteristics and behaviors. Use the `Config^` singleton class (from `taipy.common.config`)
to configure your application. Please refer to the
[data nodes](../../../../userman/scenario_features/data-integration/data-node-config.md),
[tasks](../../../../userman/scenario_features/task-orchestration/scenario-config.md),
and [scenarios](../../../../userman/scenario_features/sdm/scenario/scenario-config.md) pages.

Once your application is configured, import module `import taipy as tp` so you can use any function described
in the following section on [Function](#functions). In particular, the most used functions are `tp.create_scenario()`,
`tp.get_scenarios()`, `tp.get_data_nodes()`, `tp.submit()`, used to get, create, and submit entities.

!!! Note

    Taipy provides a runnable service, `Orchestrator^` that runs as a service in a dedicated thread.
    The purpose is to have a dedicated thread responsible for dispatching the submitted jobs to an available
    executor for their execution.

    In particular, this `Orchestrator^` service is automatically run when used with Taipy REST or Taipy GUI.
    See the [running services](../../../../userman/run-deploy/run/running_services.md) page of the user
    manual for more details.
"""

from ._init import *
from ._init_version import _read_version
from .common.mongo_default_document import MongoDefaultDocument
from .data.data_node_id import Edit
from .exceptions import exceptions

__version__ = _read_version()
