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
export type Cycle = [string, string, Scenarios | DataNodes, number, boolean];
export type Cycles = Array<Cycle>;

export enum NodeType {
    CYCLE = 0,
    SCENARIO = 1,
    PIPELINE = 2,
    NODE = 3,
}

// job id, job name, entity id, entity name, submit id, creation date, status
export type Job = [string, string, string, string, string, string, number];
export type Jobs = Array<Job>;

export enum JobStatus {
    COMPLETED = 0,
    SUBMITTED = 1,
    BLOCKED = 2,
    PENDING = 3,
    RUNNING = 4,
    CANCELED = 5,
    FAILED = 6,
    SKIPPED = 7,
    ABANDONED = 8,
}
