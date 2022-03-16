from __future__ import annotations

from typing import List


class _EntityIds:
    def __init__(self):
        self.data_node_ids = set()
        self.task_ids = set()
        self.scenario_ids = set()
        self.pipeline_ids = set()
        self.job_ids = set()

    def __add__(self, other: _EntityIds):
        self.data_node_ids.update(other.data_node_ids)
        self.task_ids.update(other.task_ids)
        self.scenario_ids.update(other.scenario_ids)
        self.pipeline_ids.update(other.pipeline_ids)
        self.job_ids.update(other.job_ids)
        return self
