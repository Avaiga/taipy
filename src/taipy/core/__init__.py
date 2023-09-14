# Copyright 2023 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

"""# Taipy Core

The Taipy Core package is a Python library designed to build powerful, customized, data-driven back-end
applications. It provides the tools to help Python developers transform their algorithms into a
complete back-end application.
More details on the [Taipy Core](../../../manuals/core/) functionalities are available in the user manual.

To build a Taipy Core application, the first step consists of setting up the Taipy configuration to design
your application's characteristics and behaviors.
Import `Config^` from the `taipy.config^` module, then use the various methods of the `Config^` singleton class to
configure your core application. In particular, configure the
[data nodes](../../../manuals/core/config/data-node-config), [tasks](../../../manuals/core/config/task-config),
and [scenarios](../../../manuals/core/config/scenario-config).
Please refer to the [Core configuration user manual](../../../manuals/core/config/) for more information and
detailed examples.

Once your application is configured, import module `import taipy as tp` so you can use any function described
in the following [function](./#functions) section. In particular, the most used functions are `tp.create_scenario`,
`tp.get_scenarios`, `tp.get_data_nodes`, `tp.submit`, used to get, create, and submit entities.

!!! Note

    Taipy Core provides a runnable service, `Core^` that runs as a service in a dedicated thread. The purpose is to
    have a dedicated thread responsible for dispatching the submitted jobs to an available executor for their execution.

    In particular, this `Core^` service is automatically run when Core is used with taipy-rest or taipy-gui. See the
    [running services](../../../manuals/running_services/) page of the user manual for more details.

"""

from ._init import *
from ._init_version import _read_version
from .common.mongo_default_document import MongoDefaultDocument
from .data.data_node_id import Edit
from .exceptions import exceptions

__version__ = _read_version()
