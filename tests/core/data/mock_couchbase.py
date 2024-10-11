class MockCouchbaseCollection:
    def __init__(self):
        self.documents = {}

    def insert(self, doc_id, document):
        if doc_id in self.documents:
            raise Exception(f"Document with ID {doc_id} already exists.")
        self.documents[doc_id] = document

    def upsert(self, doc_id, document):
        self.documents[doc_id] = document

    def get(self, doc_id):
        if doc_id not in self.documents:
            raise Exception(f"Document with ID {doc_id} not found.")
        return self.documents[doc_id]

    def remove(self, doc_id):
        if doc_id not in self.documents:
            raise Exception(f"Document with ID {doc_id} not found.")
        del self.documents[doc_id]

class MockCouchbaseBucket:
    def __init__(self):
        self.collection = MockCouchbaseCollection()

    def collection(self, name):
        return self.collection


class MockCouchbaseCluster:
    def __init__(self):
        self.bucket = MockCouchbaseBucket()

    def bucket(self, name):
        return self.bucket

# Usage example
if __name__ == "__main__":
    cluster = MockCouchbaseCluster()
    bucket = cluster.bucket("test_bucket")
    collection = bucket.collection("test_collection")

    # Insert a document
    collection.insert("doc1", {"name": "Test Document"})

    # Get the document
    doc = collection.get("doc1")
    print(doc)  # Output: {'name': 'Test Document'}

    # Update the document
    collection.upsert("doc1", {"name": "Updated Document"})

    # Get the updated document
    updated_doc = collection.get("doc1")
    print(updated_doc)  # Output: {'name': 'Updated Document'}

    # Remove the document
    collection.remove("doc1")
