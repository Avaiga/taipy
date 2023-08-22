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

"""# Taipy Rest

The Taipy Rest package exposes the Runnable `Rest^` service to provide REST APIs on top of Taipy Core. (more details
on Taipy Core functionalities in the [user manual](../../../manuals/core/)).

Once the `Rest^` service runs, users can call REST APIs to create, read, update, submit and remove Taipy entities
(including cycles, scenarios, sequences, tasks, jobs, and data nodes). It is handy when it comes to integrating a
Taipy application in a more complex IT ecosystem.

Please refer to [REST API](../../reference_rest/) page to get the exhaustive list of available APIs."""

from ._init import *
from .version import _get_version

__version__ = _get_version()
