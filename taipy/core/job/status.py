# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from taipy.core.common._repr_enum import _ReprEnum


class Status(_ReprEnum):
    """Execution status of a `Job^`.

    It is implemented as an enumeration.
    
    The possible values are:

    - `SUBMITTED`: A `SUBMITTED` job has been submitted for execution but not processed yet by
        the scheduler.

    - `PENDING`: A `PENDING` job has been enqueued by the scheduler. It is waiting for an executor
        to be available for its execution.

    - `BLOCKED`: A `BLOCKED` job has been blocked because its input data nodes are not ready yet.
        It is waiting for the completion of another `Job^`

    - `RUNNING`: A `RUNNING` job is currently executed by a dedicated executor.

    - `CANCELLED`: A `CANCELLED` job has been submitted but its execution has been cancelled.

    - `FAILED`: A `FAILED` job raised an exception during its execution.

    - `COMPLETED`: A `COMPLETED` job has successfully been executed.

    - `SKIPPED`: A `SKIPPED` job has not been executed because its outputs were already computed.
    """

    SUBMITTED = 1
    BLOCKED = 2
    PENDING = 3
    RUNNING = 4
    CANCELLED = 5
    FAILED = 6
    COMPLETED = 7
    SKIPPED = 8
