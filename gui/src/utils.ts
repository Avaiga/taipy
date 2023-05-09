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

// id, is_primary, config_id, creation_date, label, tags, properties(key, value), pipelines(id, label), authorized_tags
export type ScenarioFull = [
  string,
  boolean,
  string,
  string,
  string,
  string[],
  Array<[string, string]>,
  Array<[string, string]>,
  string[]
];

export interface ScenarioDict {
  config: string;
  name: string;
  date: string;
  properties: Array<[string, string]>;
}

export type Property = {
  id: string;
  key: string;
  value: string;
};

export type Scenario = [string, string, undefined, number, boolean];
export type Scenarios = Array<Scenario>;
export type Cycles = Array<[string, string, Scenarios, number, boolean]>;
