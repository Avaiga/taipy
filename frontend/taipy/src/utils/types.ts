export type DisplayModel = [
    string,
    Record<string, Record<string, { name: string; type: string, status?: TaskStatus }>>,
    Array<[string, string, string, string]>
];

export type DataNode = [string, string, undefined, number, boolean];
export type DataNodes = Array<DataNode>;
export type Sequence = [string, string, DataNodes, number, boolean];
export type Sequences = Array<Sequence>;
export type Scenario = [string, string, DataNodes | Sequences, number, boolean];
export type Scenarios = Array<Scenario>;
export type Cycle = [string, string, Scenarios | DataNodes, number, boolean];
export type Cycles = Array<Cycle>;

export enum NodeType {
    CYCLE = 0,
    SCENARIO = 1,
    SEQUENCE = 2,
    NODE = 3,
}

export enum TaskStatus {
    Quiet = 0,
    Pending = 3,
    Running = 4,
}

export type TaskStatuses = Record<string, TaskStatus>;
