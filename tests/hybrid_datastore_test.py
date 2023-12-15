import unittest
from unittest.mock import patch
from datastore.hybrid_datastore import HybridDataStore
from models.models import Document, BucketObject, Bucket

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
        # Set up mock environment variables for MinIO
        self.env_patcher = patch.dict('os.environ', {
            'MINIO_URL': 'http://localhost:9000',
            'MINIO_ACCESS_KEY': 'minioadmin',
            'MINIO_SECRET_KEY': 'minioadmin',
            # Add other necessary MinIO environment variables
        })
        self.env_patcher.start()

        # Replace actual MinIO and Weaviate clients with mocks
        self.hybrid_store = HybridDataStore()
        self.hybrid_store.minio_store = MockMinIO()
        self.hybrid_store.weaviate_store = MockWeaviate()

    def tearDown(self):
        self.env_patcher.stop()

    async def test_batch_ingest_from_bucket(self):
        # Test batch ingest functionality - note the 'await' keyword
        result = await self.hybrid_store.batch_ingest_from_bucket("my_bucket")
        self.assertIn("sample.txt", result)  # Check if sample.txt object was ingested

    async def test_upsert(self):
        # Test the upsert function with sample data - note the 'await' keyword
        documents = [Document(id="doc1", text="Sample text")]
        result = await self.hybrid_store.upsert(documents)
        self.assertIn("doc1", result)  # Check if doc1 is in the result

# Running the tests
if __name__ == '__main__':
    unittest.main()
