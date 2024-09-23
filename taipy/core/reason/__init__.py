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
"""Reasons for the Taipy actions why they can't be performed.

Because Taipy applications are natively multiuser, asynchronous, and dynamic,
some functions might not be called in some specific contexts. You can protect
such calls by calling other methods that return a `ReasonCollection^`. It acts
like a boolean: True if the operation can be performed and False otherwise. If
the action cannot be performed, the `ReasonCollection^` holds all the individual
reasons as a list of `Reason` objects.

This package `taipy.core.reason` exposes the `ReasonCollection^` class and all
the reason implementations that can be used to explain why some Taipy operations
is not allowed.
"""

from .reason import (
    DataNodeEditInProgress,
    DataNodeIsNotWritten,
    EntityDoesNotExist,
    EntityIsNotSubmittableEntity,
    InvalidUploadFile,
    JobIsNotFinished,
    NoFileToDownload,
    NotAFile,
    NotGlobalScope,
    Reason,
    ScenarioDoesNotBelongToACycle,
    ScenarioIsThePrimaryScenario,
    SubmissionIsNotFinished,
    SubmissionStatusIsUndefined,
    UploadFileCanNotBeRead,
    WrongConfigType,
)
from .reason_collection import ReasonCollection
