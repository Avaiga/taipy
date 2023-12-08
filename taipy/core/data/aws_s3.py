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


import boto3
from datetime import datetime, timedelta
from inspect import isclass
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from taipy.config.common.scope import Scope

from .._version._version_manager_factory import _VersionManagerFactory
from ..exceptions.exceptions import InvalidCustomDocument, MissingRequiredProperty
from .data_node import DataNode
from .data_node_id import DataNodeId, Edit


class S3ObjectDataNode(DataNode):
    """Data Node object stored in an Amazon Web Service S3 Bucket.

    Attributes:
        config_id (str): Identifier of the data node configuration. It must be a valid Python
            identifier.
        scope (Scope^): The scope of this data node.
        id (str): The unique identifier of this data node.
        owner_id (str): The identifier of the owner (sequence_id, scenario_id, cycle_id) or
            None.
        parent_ids (Optional[Set[str]]): The identifiers of the parent tasks or `None`.
        last_edit_date (datetime): The date and time of the last modification.
        edits (List[Edit^]): The ordered list of edits for that job.
        version (str): The string indicates the application version of the data node to instantiate. If not provided,
            the current version is used.
        validity_period (Optional[timedelta]): The duration implemented as a timedelta since the last edit date for
            which the data node can be considered up-to-date. Once the validity period has passed, the data node is
            considered stale and relevant tasks will run even if they are skippable (see the
            [Task management page](../core/entities/task-mgt.md) for more details).
            If _validity_period_ is set to `None`, the data node is always up-to-date.
        edit_in_progress (bool): True if a task computing the data node has been submitted
            and not completed yet. False otherwise.
        editor_id (Optional[str]): The identifier of the user who is currently editing the data node.
        editor_expiration_date (Optional[datetime]): The expiration date of the editor lock.
        properties (dict[str, Any]): A dictionary of additional properties. Note that the
            _properties_ parameter must at least contain an entry for _"aws_access_key"_ , _"aws_secret_access_key"_ ,
            _aws_s3_bucket_name_ and _aws_s3_object_key_ :

            - _"aws_access_key"_ `(str)`: Amazon Web Services ID for to identify account\n
            - _"aws_secret_access_key"_ `(str)`: Amazon Web Services access key to authenticate programmatic requests.\n
            - _"aws_region"_ `(Any)`: Self-contained geographic area where Amazon Web Services (AWS) infrastructure is
                    located.\n
            - _"aws_s3_bucket_name"_ `(str)`: unique identifier for a container that stores objects in Amazon Simple
                    Storage Service (S3).\n
            - _"aws_s3_object_key"_ `(str)`:  unique idntifier for the name of the object(file) that has to be read
                    or written. \n
            - _"aws _s3_object_parameters"_ `(str)`: A dictionary of additional arguments to be passed to interact with
                    the AWS service\n

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
    ):
        if properties is None:
            properties = {}
        required = self._REQUIRED_PROPERTIES
        if missing := set(required) - set(properties.keys()):
            raise MissingRequiredProperty(
                f"The following properties " f"{', '.join(x for x in missing)} were not informed and are required."
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
            's3',
            aws_access_key_id=properties.get(self.__AWS_ACCESS_KEY_ID),
            aws_secret_access_key=properties.get(self.__AWS_SECRET_ACCESS_KEY),
        )

        if not self._last_edit_date:
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
        return cls.__STORAGE_TYPE

    def _read(self):
        aws_s3_object = self._s3_client.get_object(
            Bucket=self.properties[self.__AWS_STORAGE_BUCKET_NAME],
            Key=self.properties[self.__AWS_S3_OBJECT_KEY],
        )
        return aws_s3_object['Body'].read().decode('utf-8')

    def _write(self, data: Any):
        self._s3_client.put_object(
            Bucket=self.properties[self.__AWS_STORAGE_BUCKET_NAME],
            Key=self.properties[self.__AWS_S3_OBJECT_KEY],
            Body=data,
        )
