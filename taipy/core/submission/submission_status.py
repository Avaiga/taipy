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


class SubmissionStatus(_ReprEnum):
    """Execution status of a `Submission^`.

    It is implemented as an enumeration.

    The possible values are:

    - `SUBMITTED`: A `SUBMITTED` submission has been submitted for execution but not processed yet by
        the orchestrator.

    - `UNDEFINED`: AN `UNDEFINED` submission's jobs have been submitted for execution but got some undefined
        status changes.

    - `PENDING`: A `PENDING` submission has been enqueued by the orchestrator. It is waiting for an executor
        to be available for its execution.

    - `BLOCKED`: A `BLOCKED` submission has been blocked because it has been finished with a job being blocked.

    - `RUNNING`: A `RUNNING` submission has its jobs currently being executed.

    - `CANCELED`: A `CANCELED` submission has been submitted but its execution has been canceled.

    - `FAILED`: A `FAILED` submission has a job failed during its execution.

    - `COMPLETED`: A `COMPLETED` submission has successfully been executed.
    """

    SUBMITTED = 0
    UNDEFINED = 1
    BLOCKED = 2
    PENDING = 3
    RUNNING = 4
    CANCELED = 5
    FAILED = 6
    COMPLETED = 7
