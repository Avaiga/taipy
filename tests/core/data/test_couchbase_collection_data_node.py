
import pytest
from mocks.mock_couchbase import MockCouchbaseCollectionDataNode
from unittest.mock import patch, MagicMock
from taipy.core.data.couchbase_collection_datanode import CouchBaseCollectionDataNode
from taipy.exceptions.exceptions import MissingRequiredProperty


# Sample properties for initializing CouchBaseCollectionDataNode
PROPERTIES = {
    "db_name": "test_db",
    "collection_name": "test_collection",
    "db_username": "username",
    "db_password": "password",
    "db_host": "localhost",
    "db_port": 8091,
}

# Test class for CouchBaseCollectionDataNode
class TestCouchBaseCollectionDataNode:

    @patch('taipy.core.data.couchbase_collection_datanode.Cluster')
    @patch('taipy.core.data.couchbase_collection_datanode.PasswordAuthenticator')
    def test_init_valid_properties(self, mock_authenticator, mock_cluster):
        """Test initialization with valid properties."""
        mock_cluster.return_value.bucket.return_value.collection.return_value = MagicMock()
        
        node = CouchBaseCollectionDataNode(
            config_id='test_config',
            scope=None,
            properties=PROPERTIES
        )
        
        assert node.storage_type() == "couchbase_collection"
        assert node.collection is not None

    def test_init_missing_properties(self):
        """Test initialization raises error for missing required properties."""
        with pytest.raises(MissingRequiredProperty):
            CouchBaseCollectionDataNode(
                config_id='test_config',
                scope=None,
                properties={"collection_name": "test_collection"}  # Missing db_name
            )

    @patch('taipy.core.data.couchbase_collection_datanode.Cluster')
    @patch('taipy.core.data.couchbase_collection_datanode.PasswordAuthenticator')
    def test_read(self, mock_authenticator, mock_cluster):
        """Test the read method returns documents."""
        mock_document = MagicMock()
        mock_document.content_as.return_value = {"key": "value"}
        mock_cluster.return_value.bucket.return_value.collection.return_value.get.return_value = mock_document
        
        node = CouchBaseCollectionDataNode(
            config_id='test_config',
            scope=None,
            properties=PROPERTIES
        )
        
        # Simulate reading from the collection
        documents = node._read()
        
        assert len(documents) == 1
        assert documents[0] == {"key": "value"}

    @patch('taipy.core.data.couchbase_collection_datanode.Cluster')
    @patch('taipy.core.data.couchbase_collection_datanode.PasswordAuthenticator')
    def test_read_empty(self, mock_authenticator, mock_cluster):
        """Test the read method returns an empty list when no documents exist."""
        mock_cluster.return_value.bucket.return_value.collection.return_value.get.side_effect = Exception("No documents found")
        
        node = CouchBaseCollectionDataNode(
            config_id='test_config',
            scope=None,
            properties=PROPERTIES
        )
        
        # Simulate reading from the collection
        documents = node._read()
        
        assert documents == []
