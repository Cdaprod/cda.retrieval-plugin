import pytest
from datastore.hybrid_datastore import HybridDataStore
from models.models import Document, BucketObject, Bucket

# Mocks for MinIO and Weaviate to simulate their behavior
class MockMinIO:
    def __init__(self):
        self.bucket_name = "mock_bucket"
        
    def upload_object(self, bucket_name, object_name, file_path):
        # Simulate upload functionality
        pass

    def list_objects(self, bucket_name):
        return [BucketObject(id="1", object_name="sample.txt", object_type="text", size=1024)] 

class MockWeaviate:
    def upsert(self, documents):
        # Simulate upsert functionality
        return ["doc1", "doc2"]

@pytest.fixture
def hybrid_store():
    store = HybridDataStore()
    store.minio_store = MockMinIO()
    store.weaviate_store = MockWeaviate()
    return store

@pytest.mark.asyncio
async def test_batch_ingest_from_bucket(hybrid_store):
    result = await hybrid_store.batch_ingest_from_bucket("my_bucket")
    assert "sample.txt" in result

@pytest.mark.asyncio
async def test_upsert(hybrid_store):
    documents = [Document(id="doc1", text="Sample text")]
    result = await hybrid_store.upsert(documents)
    assert "doc1" in result
