import pytest
from datetime import datetime
from taipy.core.data.couchbase_collection_datanode import CouchBaseCollectionDataNode
from taipy.common.config.common.scope import Scope

# Define some basic test properties
test_properties = {
    "db_name": "test_db",
    "collection_name": "test_collection",
    "db_host": "localhost",
    "db_port": "8091",
    "db_username": "admin",
    "db_password": "password"
}

def test_couchbase_datanode_initialization():
    node = CouchBaseCollectionDataNode("test_node", Scope.GLOBAL, properties=test_properties)
    assert node.storage_type() == "couchbase_collection"
    assert node.properties["db_name"] == "test_db"
    assert node.properties["collection_name"] == "test_collection"
    assert node.collection is not None

def test_couchbase_datanode_write_and_read():
    node = CouchBaseCollectionDataNode("test_node", Scope.GLOBAL, properties=test_properties)
    test_data = {"name": "John Doe", "age": 30}
    node._write([test_data])  # Insert the test data into Couchbase
    data = node._read()
    assert len(data) == 1
    assert data[0]["name"] == "John Doe"
    assert data[0]["age"] == 30
