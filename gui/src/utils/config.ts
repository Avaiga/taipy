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

import { DataNode, Sequence, Scenario, Task } from "./names";

const nodeColor: Record<string, string> = {
  [DataNode]: "#283282",
  [Task]: "#ff462b",
  [Sequence]: "#ff462b",
  [Scenario]: "#f0faff",
};
export const getNodeColor = (nodeType: string) => nodeColor[nodeType] || "pink";

const nodeIcon: Record<string, string> = {
  [DataNode]: "datanode",
  [Task]: "task",
  [Sequence]: "sequence",
  [Scenario]: "scenario",
};
export const getNodeIcon = (nodeType: string) => nodeIcon[nodeType];

export const nodeTypes = [DataNode, Sequence, Scenario, Task];
