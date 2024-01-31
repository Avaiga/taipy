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

from datetime import datetime

from .._repository._abstract_converter import _AbstractConverter
from ..job.job import Job, JobId
from ..submission._submission_model import _SubmissionModel
from ..submission.submission import Submission
from .submission import SubmissionId


class _SubmissionConverter(_AbstractConverter):
    @classmethod
    def _entity_to_model(cls, submission: Submission) -> _SubmissionModel:
        return _SubmissionModel(
            id=submission.id,
            entity_id=submission._entity_id,
            entity_type=submission.entity_type,
            entity_config_id=submission._entity_config_id,
            job_ids=[job.id if isinstance(job, Job) else JobId(str(job)) for job in list(submission._jobs)],
            properties=submission._properties.data.copy(),
            creation_date=submission._creation_date.isoformat(),
            submission_status=submission._submission_status,
            version=submission._version,
            is_abandoned=submission._is_abandoned,
            is_completed=submission._is_completed,
            is_canceled=submission._is_canceled,
            running_jobs=list(submission._running_jobs),
            blocked_jobs=list(submission._blocked_jobs),
            pending_jobs=list(submission._pending_jobs),
        )

    @classmethod
    def _model_to_entity(cls, model: _SubmissionModel) -> Submission:
        submission = Submission(
            entity_id=model.entity_id,
            entity_type=model.entity_type,
            entity_config_id=model.entity_config_id,
            id=SubmissionId(model.id),
            jobs=model.job_ids,
            properties=model.properties,
            creation_date=datetime.fromisoformat(model.creation_date),
            submission_status=model.submission_status,
            version=model.version,
        )

        submission._is_abandoned = model.is_abandoned
        submission._is_completed = model.is_completed
        submission._is_canceled = model.is_canceled

        submission._running_jobs = set(model.running_jobs)
        submission._blocked_jobs = set(model.blocked_jobs)
        submission._pending_jobs = set(model.pending_jobs)

        return submission
