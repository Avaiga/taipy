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
from .._repository._filesystem_repository import _FileSystemRepository
from ._job_converter import _JobConverter
from ._job_model import _JobModel


class _JobFSRepository(_FileSystemRepository):
    def __init__(self) -> None:
        super().__init__(model_type=_JobModel, converter=_JobConverter, dir_name="jobs")
