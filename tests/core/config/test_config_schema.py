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

import json

import pytest
from jsonschema import ValidationError, validate

with open("taipy/core/config/config.schema.json", "r") as f:
    json_schema = json.load(f)


def test_validate_generic_datanode_config():
    generic_cfg_without_read_write_fct = {"DATA_NODE": {"properties": {"storage_type": "generic"}}}
    with pytest.raises(ValidationError):
        validate(generic_cfg_without_read_write_fct, json_schema)

    generic_cfg_without_write_fct = {
        "DATA_NODE": {"properties": {"storage_type": "generic", "read_fct": "module.read_fct"}}
    }
    with pytest.raises(ValidationError):
        validate(generic_cfg_without_write_fct, json_schema)

    generic_cfg_without_read_fct = {
        "DATA_NODE": {"properties": {"storage_type": "generic", "write_fct": "module.write_fct"}}
    }
    with pytest.raises(ValidationError):
        validate(generic_cfg_without_read_fct, json_schema)

    generic_cfg_with_read_write_fct = {
        "DATA_NODE": {
            "properties": {"storage_type": "generic", "read_fct": "module.read_fct", "write_fct": "module.write_fct"}
        }
    }
    validate(generic_cfg_with_read_write_fct, json_schema)


def test_validate_sql_datanode_config():
    sql_cfg_sqlite_without_required_properties = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql",
                "db_engine": "sqlite",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(sql_cfg_sqlite_without_required_properties, json_schema)

    sql_cfg_sqlite = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql",
                "db_engine": "sqlite",
                "db_name": "name",
                "read_query": "SELECT * FROM table",
                "write_query_builder": "module.write_query_builder",
            }
        }
    }
    validate(sql_cfg_sqlite, json_schema)

    sql_cfg_notsqlite_without_required_properties = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql",
                "db_engine": "mysql",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(sql_cfg_notsqlite_without_required_properties, json_schema)

    sql_cfg_notsqlite_without_username_password = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql",
                "db_engine": "mysql",
                "db_name": "name",
                "read_query": "SELECT * FROM table",
                "write_query_builder": "module.write_query_builder",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(sql_cfg_notsqlite_without_username_password, json_schema)

    sql_cfg_notsqlite = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql",
                "db_engine": "mysql",
                "db_name": "name",
                "db_username": "user",
                "db_password": "pass",
                "read_query": "SELECT * FROM table",
                "write_query_builder": "module.write_query_builder",
            }
        }
    }
    validate(sql_cfg_notsqlite, json_schema)


def test_validate_sql_table_datanode_config():
    sql_table_cfg_sqlite_without_required_properties = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql_table",
                "db_engine": "sqlite",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(sql_table_cfg_sqlite_without_required_properties, json_schema)

    sql_table_cfg_sqlite = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql_table",
                "db_engine": "sqlite",
                "db_name": "name",
                "table_name": "table",
            }
        }
    }
    validate(sql_table_cfg_sqlite, json_schema)

    sql_table_cfg_notsqlite_without_required_properties = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql_table",
                "db_engine": "mysql",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(sql_table_cfg_notsqlite_without_required_properties, json_schema)

    sql_table_cfg_notsqlite_without_username_password = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql_table",
                "db_engine": "mysql",
                "db_name": "name",
                "table_name": "table",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(sql_table_cfg_notsqlite_without_username_password, json_schema)

    sql_table_cfg_notsqlite = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "sql_table",
                "db_engine": "mysql",
                "db_name": "name",
                "db_username": "user",
                "db_password": "pass",
                "table_name": "table",
            }
        }
    }
    validate(sql_table_cfg_notsqlite, json_schema)


def test_validate_mongo_collection_datanode_config():
    mongo_collection_cfg_without_required_properties = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "mongo_collection",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(mongo_collection_cfg_without_required_properties, json_schema)

    mongo_collection_cfg = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "mongo_collection",
                "db_name": "name",
                "collection_name": "collection",
            }
        }
    }
    validate(mongo_collection_cfg, json_schema)


def test_validate_s3_object_datanode_config():
    s3_object_cfg_without_required_properties = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "s3_object",
            }
        }
    }
    with pytest.raises(ValidationError):
        validate(s3_object_cfg_without_required_properties, json_schema)

    s3_object_cfg = {
        "DATA_NODE": {
            "properties": {
                "storage_type": "s3_object",
                "aws_access_key": "access_key",
                "aws_secret_access_key": "secret_access_key",
                "aws_s3_bucket_name": "bucket",
                "aws_s3_object_key": "object_key",
            }
        }
    }
    validate(s3_object_cfg, json_schema)
