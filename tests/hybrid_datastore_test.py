import unittest
from datastore.hybrid_datastore import HybridDataStore, Document, BucketObject, Bucket

# Mocks for MinIO and Weaviate to simulate their behavior
class MockMinIO:
    def upload_object(self, bucket_name, object_name, file_path):
        # Simulate upload functionality
        pass

    def list_objects(self, bucket_name):
        return [BucketObject(object_name="sample.txt", object_type="text", size=1024)]

class MockWeaviate:
    def upsert(self, documents):
        # Simulate upsert functionality
        return ["doc1", "doc2"]

# The unit test class
class TestHybridDataStore(unittest.TestCase):
    def setUp(self):
        # Replace actual MinIO and Weaviate clients with mocks
        self.hybrid_store = HybridDataStore()
        self.hybrid_store.minio_store = MockMinIO()
        self.hybrid_store.weaviate_store = MockWeaviate()

    def test_upsert(self):
        # Test the upsert function with sample data
        documents = [Document(id="doc1", text="Sample text")]
        result = self.hybrid_store.upsert(documents)
        self.assertIn("doc1", result)  # Check if doc1 is in the result

    def test_batch_ingest_from_bucket(self):
        # Test batch ingest functionality
        result = self.hybrid_store.batch_ingest_from_bucket("my_bucket")
        self.assertIn("sample.txt", result)  # Check if sample.txt object was ingested

# Running the tests
if __name__ == '__main__':
    unittest.main()

#poetry run pytest tests/hybrid_datastore_test.py::TestHybridDataStore 