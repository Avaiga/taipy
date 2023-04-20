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
    label: "Cycle 2023-02-04",
    type: 0,
    primary: false,
    children: [
      {
        id: "scenario_1.1",
        label: "Scenario 1.1",
        type: 1,
        primary: true,
      },
      {
        id: "scenario_1.2",
        label: "Scenario 1.2",
        type: 1,
        primary: false,
      },
      {
        id: "scenario_1.3",
        label: "Scenario 1.3",
        type: 1,
        primary: false,
      },
    ],
  },
  {
    id: "cycle_2",
    label: "Cycle 2023-02-05",
    type: 0,
    primary: false,
    children: [
      {
        id: "scenario_2.1",
        label: "Scenario 2.1",
        type: 1,
        primary: true,
      },
      {
        id: "scenario_2.2",
        label: "Scenario 2.2",
        type: 1,
        primary: false,
      },
      {
        id: "scenario_2.3",
        label: "Scenario 2.3",
        type: 1,
        primary: false,
      },
    ],
  },
  {
    id: "cycle_3",
    label: "Cycle 2023-02-06",
    type: 0,
    primary: false,
    children: [
      {
        id: "scenario_3.1",
        label: "Scenario 3.1",
        type: 1,
        primary: true,
      },
      {
        id: "scenario_3.2",
        label: "Scenario 3.2",
        type: 1,
        primary: false,
      },
      {
        id: "scenario_3.3",
        label: "Scenario 3.3",
        type: 1,
        primary: false,
      },
    ],
  },
  {
    id: "cycle_4",
    label: "Cycle 2023-02-07",
    type: 0,
    primary: false,
    children: [
      {
        id: "scenario_4.1",
        label: "Scenario 4.1",
        type: 1,
        primary: true,
      },
      {
        id: "scenario_4.2",
        label: "Scenario 4.2",
        type: 1,
        primary: false,
      },
      {
        id: "scenario_4.3",
        label: "Scenario 4.3",
        type: 1,
        primary: false,
      },
    ],
  },
  {
    id: "scenario_5",
    label: "Scenario 5",
    type: 1,
    primary: false,
  },
];
