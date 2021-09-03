from dataclasses import dataclass

from taipy.pipeline.types import PipelineId, Dag


@dataclass
class PipelineSchema:
    id: PipelineId
    name: str
    properties: dict
    dag: Dag
    # The dag dictionary represents the successors of each node (data source or task),
    # including the leaf nodes without successors.
    #
    # dag_example = { data_source_id_1: [task_id_A],
    #   task_id_A: [data_source_id_2],
    #   data_source_id_2: [task_id_B],
    #   data_source_id_3: [task_id_B],
    #   task_id_B: [data_source_id_4],
    #   data_source_id_4: [task_id_c],
    #   task_id_c: [data_source_id_5, data_source_id_6],
    #   data_source_id_5: [],
    #   data_source_id_6: []
    # }
    #
    #   1 --> A --> 2 -----> B --> 4 --> C -----> 5
    #                   |                     |
    #               3 ---                     --> 6