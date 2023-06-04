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


def migrate_subscriber(fct_module, fct_name):
    """Rename scheduler by orchestrator on old jobs. Used to migrate from <=2.2 to >=2.3 version."""

    if fct_module == "taipy.core._scheduler._scheduler":
        fct_module = fct_module.replace("_scheduler", "_orchestrator")
        fct_name = fct_name.replace("_Scheduler", "_Orchestrator")
    return fct_module, fct_name
