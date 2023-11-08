# Copyright 2023 Avaiga Private Limited
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
            job_ids=[job.id if isinstance(job, Job) else JobId(str(job)) for job in list(submission._jobs)],
            creation_date=submission._creation_date.isoformat(),
            submission_status=submission._submission_status,
        )

    @classmethod
    def _model_to_entity(cls, model: _SubmissionModel) -> Submission:
        submission = Submission(
            entity_id=model.entity_id,
            jobs=model.job_ids,
            submission_id=SubmissionId(model.id),
        )
        submission._creation_date = datetime.fromisoformat(model.creation_date)
        submission._submission_status = model.submission_status
        return submission
