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
