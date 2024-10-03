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

from abc import ABC

from .section import Section


class UniqueSection(Section, ABC):
    """An abstract class representing a subdivision of the configuration class `Config^`.

    Each UniqueSection implementation class defines a semantically consistent set of settings
    related to a particular aspect of the application. It differs from a regular `Section` in
    that it is designed to be unique, meaning only one instance can exist. Each UniqueSection
    is defined by a section name (related to the objects they configure) and a set of properties.

    Here are the various unique sections in Taipy:

    - `GlobalAppConfig^` for configuring global application settings.
    - `GuiSection` for configuring the GUI service.
    - `CoreSection^` for configuring the core package behavior.
    - `JobConfig^` for configuring the job orchestration.
    - `AuthenticationConfig^` for configuring authentication settings.

    """

    def __init__(self, **properties):
        super().__init__(self.name, **properties)
