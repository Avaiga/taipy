export type DisplayModel = [
    string,
    Record<string, Record<string, { name: string; type: string }>>,
    Array<[string, string, string, string]>
];

export type Node = [string];
export type Scenario = [string, string, undefined, number, boolean];
export type Scenarios = Array<Scenario>;
export type Cycles = Array<[string, string, Scenario, number, boolean]>;

export enum NodeType {
    CYCLE = 0,
    SCENARIO = 1,
    PIPELINE = 2,
    NODE = 3,
}
