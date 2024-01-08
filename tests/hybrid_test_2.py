import pytest
from datastore.hybrid_datastore import HybridDataStore
from models.models import Document, BucketObject, Bucket

# Assuming MockMinIO and MockWeaviate are defined elsewhere

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
