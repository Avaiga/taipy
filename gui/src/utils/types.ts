export type DisplayModel = [
    string,
    Record<string, Record<string, { name: string; type: string }>>,
    Array<[string, string, string, string]>
];

export type DataNode = [string, string, undefined, number, boolean];
export type DataNodes = Array<DataNode>;
export type Pipeline = [string, string, DataNodes, number, boolean];
export type Pipelines = Array<Pipeline>;
export type Scenario = [string, string, DataNodes | Pipelines, number, boolean];
export type Scenarios = Array<Scenario>;
export type Cycles = Array<[string, string, Scenarios | DataNodes, number, boolean]>;

export enum NodeType {
    CYCLE = 0,
    SCENARIO = 1,
    PIPELINE = 2,
    NODE = 3,
}
