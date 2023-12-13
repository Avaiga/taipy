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

import os
from dataclasses import dataclass
from unittest.mock import patch

import boto3
from moto import mock_s3
import pytest

from taipy.core.data.data_node_id import DataNodeId
from taipy.core.data.aws_s3 import S3ObjectDataNode
from taipy.core.exceptions.exceptions import InvalidCustomDocument, MissingRequiredProperty
from taipy.config.common.scope import Scope


class TestS3ObjectDataNode:
    __properties = [
        {
            "aws_access_key": "testing",
            "aws_secret_access_key": "testing",
            "aws_s3_bucket_name": "taipy",
            "aws_s3_object_key": " taipy-object",
            "aws_region": "us-east-1",
            "aws_s3_object_parameters": {},
        }
    ]

    @mock_s3
    @pytest.mark.parametrize("properties", __properties)
    def test_create(self, properties):
        aws_s3_object_dn = S3ObjectDataNode(
            "foo_bar_aws_s3",
            Scope.SCENARIO,
            properties=properties,
        )
        assert isinstance(aws_s3_object_dn, S3ObjectDataNode)
        assert aws_s3_object_dn.storage_type() == "s3_object"
        assert aws_s3_object_dn.config_id == "foo_bar_aws_s3"
        assert aws_s3_object_dn.scope == Scope.SCENARIO
        assert aws_s3_object_dn.id is not None
        assert aws_s3_object_dn.owner_id is None
        assert aws_s3_object_dn.job_ids == []
        assert aws_s3_object_dn.is_ready_for_reading

    @mock_s3
    @pytest.mark.parametrize(
        "data",
        [
            ("Hello, write world!"),
        ],
    )
    @pytest.mark.parametrize("properties", __properties)
    def test_write(self, properties, data):
        bucket_name = properties["aws_s3_bucket_name"]
        # Create an S3 client
        s3_client = boto3.client("s3")
        # Create a bucket
        s3_client.create_bucket(Bucket=bucket_name)
        # Assign a name to the object
        object_key = properties["aws_s3_object_key"]
        # Create Taipy S3ObjectDataNode
        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        # Put an object in the bucket with Taipy
        aws_s3_object_dn._write(data)
        # Read the object with boto3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        assert response["Body"].read().decode("utf-8") == "Hello, write world!"

    @mock_s3
    @pytest.mark.parametrize(
        "data",
        [
            ("Hello, read world!"),
        ],
    )
    @pytest.mark.parametrize("properties", __properties)
    def test_read(self, properties, data):
        bucket_name = properties["aws_s3_bucket_name"]
        # Create an S3 client
        client = boto3.client("s3")
        # Create a bucket
        client.create_bucket(Bucket=bucket_name)
        # Put an object in the bucket with boto3
        object_key = properties["aws_s3_object_key"]
        object_body = "Hello, read world!"
        client.put_object(Body=object_body, Bucket=bucket_name, Key=object_key)
        # Create Taipy S3ObjectDataNode
        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        # Read the Object from bucket with Taipy
        response = aws_s3_object_dn._read()

        assert response == data
