# test_couchbase_collection_datanode.py
import unittest
from mock_couchbase import MockBucket
from couchbase_collection_datanode import CouchBaseCollectionDataNode  # Make sure this import is correct


class TestCouchBaseCollectionDataNode(unittest.TestCase):
    def setUp(self):
        self.mock_bucket = MockBucket()
        self.data_node = CouchBaseCollectionDataNode(properties={}, mock_bucket=self.mock_bucket.collection)

    def test_write_document(self):
        doc_id = "doc1"
        document = {"name": "John", "age": 30}
        self.data_node._write(doc_id, document)  # Assuming _write is a method that saves a document

        retrieved_doc = self.mock_bucket.collection.get(doc_id)
        self.assertEqual(retrieved_doc, document)

    def test_append_document(self):
        doc_id = "doc2"
        document = {"name": "Jane", "hobbies": []}
        self.data_node._write(doc_id, document)  # Assuming _write is implemented correctly

        additional_data = ["reading", "hiking"]
        self.data_node._append(doc_id, additional_data)  # Assuming _append is implemented correctly

        retrieved_doc = self.mock_bucket.collection.get(doc_id)
        self.assertEqual(retrieved_doc["hobbies"], additional_data)

if __name__ == "__main__":
    unittest.main()
