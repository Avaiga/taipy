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

import os
import pathlib
import pickle
from io import BytesIO

import boto3
import pandas as pd
import pytest
from moto import mock_s3
from pandas.testing import assert_frame_equal

from taipy.config import Config
from taipy.config.common.scope import Scope
from taipy.core.data._data_manager_factory import _DataManagerFactory
from taipy.core.data.aws_s3 import S3ObjectDataNode


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

    @pytest.mark.parametrize("properties", __properties)
    def test_create(self, properties):
        s3_object_dn_config = Config.configure_s3_object_data_node(id="foo_bar_aws_s3", **properties)
        aws_s3_object_dn = _DataManagerFactory._build_manager()._create_and_set(s3_object_dn_config, None, None)
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
    def test_write_text(self, properties, data):
        bucket_name = properties["aws_s3_bucket_name"]
        s3_client = boto3.client("s3")
        # Create a bucket
        s3_client.create_bucket(Bucket=bucket_name)
        # Assign a name to the object
        object_key = properties["aws_s3_object_key"]
        # Create Taipy S3ObjectDataNode
        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        aws_s3_object_dn._write(data)
        # Read the object with boto3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)

        assert response["Body"].read().decode("utf-8") == "Hello, write world!"

    @mock_s3
    @pytest.mark.parametrize(
        "data_path",
        [
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.csv"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.xlsx"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.p"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.parquet"),
        ],
    )
    @pytest.mark.parametrize("properties", __properties)
    def test_write_binary_data(self, properties, data_path):
        bucket_name = properties["aws_s3_bucket_name"]
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=bucket_name)
        object_key = properties["aws_s3_object_key"]

        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        with open(data_path, "rb") as file_binary_data:
            aws_s3_object_dn._write(file_binary_data)

        # Read the object with boto3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        s3_data = response["Body"].read()

        if data_path.endswith(".csv"):
            assert_frame_equal(pd.read_csv(BytesIO(s3_data)), pd.read_csv(data_path))
        elif data_path.endswith(".xlsx"):
            assert_frame_equal(pd.read_excel(BytesIO(s3_data)), pd.read_excel(data_path))
        elif data_path.endswith(".parquet"):
            assert_frame_equal(pd.read_parquet(BytesIO(s3_data)), pd.read_parquet(data_path))
        elif data_path.endswith(".p"):
            assert pickle.loads(s3_data) == pickle.load(open(data_path, "rb"))

    @mock_s3
    @pytest.mark.parametrize(
        "data",
        [
            ("Hello, read world!"),
        ],
    )
    @pytest.mark.parametrize("properties", __properties)
    def test_read_text(self, properties, data):
        bucket_name = properties["aws_s3_bucket_name"]
        client = boto3.client("s3")
        # Create a bucket
        client.create_bucket(Bucket=bucket_name)
        object_key = properties["aws_s3_object_key"]
        object_body = "Hello, read world!"
        client.put_object(Body=object_body, Bucket=bucket_name, Key=object_key)
        # Create Taipy S3ObjectDataNode
        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        # Read the Object from bucket with Taipy
        response = aws_s3_object_dn._read()

        assert response.decode("utf-8") == data

    @mock_s3
    @pytest.mark.parametrize(
        "data_path",
        [
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.csv"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.xlsx"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.p"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.parquet"),
        ],
    )
    @pytest.mark.parametrize("properties", __properties)
    def test_read_binary_data(self, properties, data_path):
        bucket_name = properties["aws_s3_bucket_name"]
        client = boto3.client("s3")
        client.create_bucket(Bucket=bucket_name)
        object_key = properties["aws_s3_object_key"]

        with open(data_path, "rb") as file_binary_data:
            client.put_object(Body=file_binary_data, Bucket=bucket_name, Key=object_key)

        # Create Taipy S3ObjectDataNode
        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        # Read the Object from bucket with Taipy
        read_data = aws_s3_object_dn._read()

        if data_path.endswith(".csv"):
            assert_frame_equal(pd.read_csv(BytesIO(read_data)), pd.read_csv(data_path))
        elif data_path.endswith(".xlsx"):
            assert_frame_equal(pd.read_excel(BytesIO(read_data)), pd.read_excel(data_path))
        elif data_path.endswith(".parquet"):
            assert_frame_equal(pd.read_parquet(BytesIO(read_data)), pd.read_parquet(data_path))
        elif data_path.endswith(".p"):
            assert pickle.loads(read_data) == pickle.load(open(data_path, "rb"))

    @mock_s3
    @pytest.mark.parametrize(
        "data_path",
        [
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.csv"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.xlsx"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.p"),
            os.path.join(pathlib.Path(__file__).parent.resolve(), "data_sample", "example.parquet"),
        ],
    )
    @pytest.mark.parametrize("properties", __properties)
    def test_read_file_data(self, properties, data_path):
        bucket_name = properties["aws_s3_bucket_name"]
        client = boto3.client("s3")
        client.create_bucket(Bucket=bucket_name)
        object_key = properties["aws_s3_object_key"]

        # Upload file to S3 bucket
        client.upload_file(Filename=data_path, Bucket=bucket_name, Key=object_key)

        # Create Taipy S3ObjectDataNode
        aws_s3_object_dn = S3ObjectDataNode("foo_aws_s3", Scope.SCENARIO, properties=properties)
        # Read the file from bucket with Taipy should return the binary data of the uploaded file
        read_data = aws_s3_object_dn._read()

        if data_path.endswith(".csv"):
            assert_frame_equal(pd.read_csv(BytesIO(read_data)), pd.read_csv(data_path))
        elif data_path.endswith(".xlsx"):
            assert_frame_equal(pd.read_excel(BytesIO(read_data)), pd.read_excel(data_path))
        elif data_path.endswith(".parquet"):
            assert_frame_equal(pd.read_parquet(BytesIO(read_data)), pd.read_parquet(data_path))
        elif data_path.endswith(".p"):
            assert pickle.loads(read_data) == pickle.load(open(data_path, "rb"))
