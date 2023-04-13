/*
 * Copyright 2023 Avaiga Private Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
 * an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 */

import { TreeNode } from "./ScenarioSelector";

export const cycles: TreeNode[] = [
  {
    id: "cycle_1",
    label: "Cycle 1",
    type: "CYCLE",
    primary: false,
    date: "2022-08-15T19:21:01.871587",
    children: [
      {
        id: "scenario_1.1",
        label: "Scenario 1.1",
        type: "SCENARIO",
        primary: true,
        date: "2022-08-15T19:21:01.871587",
      },
      {
        id: "scenario_1.2",
        label: "Scenario 1.2",
        type: "SCENARIO",
        primary: false,
        date: "2022-08-15T19:21:01.871587",
      },
      {
        id: "scenario_1.3",
        label: "Scenario 1.3",
        type: "SCENARIO",
        primary: false,
        date: "2022-08-15T19:21:01.871587",
      },
    ],
  },
  {
    id: "cycle_2",
    label: "Cycle 2",
    type: "CYCLE",
    primary: false,
    date: "2022-06-15T19:21:01.871587",
    children: [
      {
        id: "scenario_2.1",
        label: "Scenario 2.1",
        type: "SCENARIO",
        primary: true,
        date: "2022-06-15T19:21:01.871587",
      },
      {
        id: "scenario_2.2",
        label: "Scenario 2.2",
        type: "SCENARIO",
        primary: false,
        date: "2022-06-15T19:21:01.871587",
      },
      {
        id: "scenario_2.3",
        label: "Scenario 2.3",
        type: "SCENARIO",
        primary: false,
        date: "2022-06-15T19:21:01.871587",
      },
    ],
  },
  {
    id: "cycle_3",
    label: "Cycle 3",
    type: "CYCLE",
    primary: false,
    date: "2022-07-15T19:21:01.871587",
    children: [
      {
        id: "scenario_3.1",
        label: "Scenario 3.1",
        type: "SCENARIO",
        primary: true,
        date: "2022-07-15T19:21:01.871587",
      },
      {
        id: "scenario_3.2",
        label: "Scenario 3.2",
        type: "SCENARIO",
        primary: false,
        date: "2022-07-15T19:21:01.871587",
      },
      {
        id: "scenario_3.3",
        label: "Scenario 3.3",
        type: "SCENARIO",
        primary: false,
        date: "2022-07-15T19:21:01.871587",
      },
    ],
  },
];
