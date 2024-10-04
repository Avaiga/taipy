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

from datetime import datetime, timedelta
from importlib import util
from typing import Any, Dict, List, Optional, Set

from ..common._check_dependencies import _check_dependency_is_installed

if util.find_spec("boto3"):
    import boto3

from taipy.common.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import MissingRequiredProperty
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class S3ObjectDataNode(DataNode):
    """Data Node object stored in an Amazon Web Service S3 Bucket.

    The *properties* attribute must contain the following required entries:

    - *aws_access_key* (`str`): Amazon Web Services ID for to identify account
    - *aws_secret_access_key* (`str`): Amazon Web Services access key to
        authenticate programmatic requests.
    - *aws_s3_bucket_name*  (`str`): unique identifier for a container that stores
        objects in Amazon Simple Storage Service (S3).
    - *aws_s3_object_key* (`str`):  unique identifier for the name of the object (file)
        that has to be read or written.

    The *properties* attribute can also contain the following optional entries:

    - *aws_region* (`Any`): Self-contained geographic area where Amazon Web Services
        (AWS) infrastructure is located.
    - *aws _s3_object_parameters* (`str`): A dictionary of additional arguments to be
        passed to interact with the AWS service
    """

    __STORAGE_TYPE = "s3_object"

    __AWS_ACCESS_KEY_ID = "aws_access_key"
    __AWS_SECRET_ACCESS_KEY = "aws_secret_access_key"
    __AWS_STORAGE_BUCKET_NAME = "aws_s3_bucket_name"
    __AWS_S3_OBJECT_KEY = "aws_s3_object_key"
    __AWS_REGION = "aws_region"
    __AWS_S3_OBJECT_PARAMETERS = "aws_s3_object_parameters"

    _REQUIRED_PROPERTIES: List[str] = [
        __AWS_ACCESS_KEY_ID,
        __AWS_SECRET_ACCESS_KEY,
        __AWS_STORAGE_BUCKET_NAME,
        __AWS_S3_OBJECT_KEY,
    ]

    def __init__(
        self,
        config_id: str,
        scope: Scope,
        id: Optional[DataNodeId] = None,
        owner_id: Optional[str] = None,
        parent_ids: Optional[Set[str]] = None,
        last_edit_date: Optional[datetime] = None,
        edits: Optional[List[Edit]] = None,
        version: str = None,
        validity_period: Optional[timedelta] = None,
        edit_in_progress: bool = False,
        editor_id: Optional[str] = None,
        editor_expiration_date: Optional[datetime] = None,
        properties: Optional[Dict] = None,
    ) -> None:
        _check_dependency_is_installed("S3 Data Node", "boto3")
        if properties is None:
            properties = {}
        required = self._REQUIRED_PROPERTIES
        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties {', '.join(missing)} were not informed and are required."
            )
        super().__init__(
            config_id,
            scope,
            id,
            owner_id,
            parent_ids,
            last_edit_date,
            edits,
            version or _VersionManagerFactory._build_manager()._get_latest_version(),
            validity_period,
            edit_in_progress,
            editor_id,
            editor_expiration_date,
            **properties,
        )

        self._s3_client = boto3.client(
            "s3",
            aws_access_key_id=properties.get(self.__AWS_ACCESS_KEY_ID),
            aws_secret_access_key=properties.get(self.__AWS_SECRET_ACCESS_KEY),
        )

        if not self._last_edit_date:  # type: ignore
            self._last_edit_date = datetime.now()

        self._TAIPY_PROPERTIES.update(
            {
                self.__AWS_ACCESS_KEY_ID,
                self.__AWS_SECRET_ACCESS_KEY,
                self.__AWS_STORAGE_BUCKET_NAME,
                self.__AWS_S3_OBJECT_KEY,
                self.__AWS_REGION,
                self.__AWS_S3_OBJECT_PARAMETERS,
            }
        )

    @classmethod
    def storage_type(cls) -> str:
        """Return the storage type of the data node: "s3_object"."""
        return cls.__STORAGE_TYPE

    def _read(self):
        properties = self.properties
        aws_s3_object = self._s3_client.get_object(
            Bucket=properties[self.__AWS_STORAGE_BUCKET_NAME],
            Key=properties[self.__AWS_S3_OBJECT_KEY],
        )
        return aws_s3_object["Body"].read()

    def _write(self, data: Any):
        properties = self.properties
        self._s3_client.put_object(
            Bucket=properties[self.__AWS_STORAGE_BUCKET_NAME],
            Key=properties[self.__AWS_S3_OBJECT_KEY],
            Body=data,
        )
