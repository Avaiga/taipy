# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

import time
from datetime import datetime

import src.taipy.core as tp
from config import scenario_cfg

if __name__ == "__main__":
    nb_scenario_to_create = 30
    init = len(tp.get_scenarios())
    print(f"init: {init}")
    for i in range(1, nb_scenario_to_create + 1):
        name = f"sc_{i}"
        start = time.perf_counter()
        scenario = tp.create_scenario(config=scenario_cfg, name=name, creation_date=datetime.now())  # type: ignore
        stop = time.perf_counter()
        print(f"scenario {i+init}/{nb_scenario_to_create+init} created in {stop - start}.")
