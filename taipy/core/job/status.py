# Copyright 2021-2024 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from ..common._repr_enum import _ReprEnum


class Status(_ReprEnum):
    """Execution status of a `Job^`.

    It is implemented as an enumeration.

    The possible values are:

    - `SUBMITTED`: A `SUBMITTED` job has been submitted for execution but not processed yet by
        the orchestrator.

    - `PENDING`: A `PENDING` job has been enqueued by the orchestrator. It is waiting for an executor
        to be available for its execution.

    - `BLOCKED`: A `BLOCKED` job has been blocked because its input data nodes are not ready yet.
        It is waiting for the completion of another `Job^`

    - `RUNNING`: A `RUNNING` job is currently executed by a dedicated executor.

    - `CANCELED`: A `CANCELED` job has been submitted but its execution has been canceled.

    - `FAILED`: A `FAILED` job raised an exception during its execution.

    - `COMPLETED`: A `COMPLETED` job has successfully been executed.

    - `SKIPPED`: A `SKIPPED` job has not been executed because its outputs were already computed.

    - `ABANDONED`: An `ABANDONED` job has not been executed because it depends on a job that could not complete (
        cancelled, failed, or abandoned).
    """

    SUBMITTED = 1
    BLOCKED = 2
    PENDING = 3
    RUNNING = 4
    CANCELED = 5
    FAILED = 6
    COMPLETED = 7
    SKIPPED = 8
    ABANDONED = 9
