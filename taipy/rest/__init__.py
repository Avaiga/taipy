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

"""# Taipy Rest

The Taipy Rest package exposes the Runnable `Rest^` service to expose REST APIs on top of Taipy Core
functionalities, in particular the scenario and data management. (more details
on the [user manual](../../../../userman/scenario_features/sdm/index.md)).

Once the `Rest^` service runs, users can call REST APIs to create, read, update, submit and remove Taipy entities
(including cycles, scenarios, sequences, tasks, jobs, and data nodes). It is handy when it comes to integrating a
Taipy application in a more complex IT ecosystem.

Please refer to [REST API](../../../reference_rest/index.md) page to get the exhaustive list of available APIs."""

from ._init import *
from .version import _get_version

__version__ = _get_version()
