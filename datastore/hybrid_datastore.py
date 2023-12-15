from models.models import BucketObject, Document, Bucket
from typing import List, Dict, Optional
import asyncio

from datastore.providers.weaviate_datastore import WeaviateDataStore
from datastore.providers.minio_datastore import MinioDataStore
from models.models import Document, DocumentChunk, Query, QueryResult, QueryWithEmbedding, DocumentMetadataFilter
from services.chunks import get_document_chunks
from services.openai import get_embeddings

class HybridDataStore:
    def __init__(self):
        self.weaviate_store = WeaviateDataStore()
        self.minio_store = MinioDataStore()

    async def upsert(self, documents: List[Document], chunk_token_size: Optional[int] = None) -> List[str]:
        """
        Processes documents: Stores raw data in MinIO and metadata in Weaviate.
        :param documents: List of Document objects to be processed and stored.
        :param chunk_token_size: Token size for chunking documents, if necessary.
        :return: List of document IDs that were processed.
        """
        # Process and store data in MinIO and metadata in Weaviate
        for document in documents:
            # Assuming document has a 'file_path' attribute for MinIO storage
            self.minio_store.upload_object(self.minio_store.bucket_name, document.id, document.file_path)

        # Chunk and store document metadata in Weaviate
        chunks = get_document_chunks(documents, chunk_token_size)
        return await self.weaviate_store._upsert(chunks)

    async def query(self, queries: List[Query]) -> List[QueryResult]:
        """
        Queries the Weaviate datastore.
        :param queries: List of Query objects.
        :return: List of QueryResult objects.
        """
        query_texts = [query.query for query in queries]
        query_embeddings = get_embeddings(query_texts)
        queries_with_embeddings = [
            QueryWithEmbedding(**query.dict(), embedding=embedding)
            for query, embedding in zip(queries, query_embeddings)
        ]
        return await self.weaviate_store._query(queries_with_embeddings)

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        filter: Optional[DocumentMetadataFilter] = None,
        delete_all: Optional[bool] = None,
    ) -> bool:
        """
        Deletes data from both Weaviate and MinIO datastores.
        :param ids: Optional list of document IDs to be deleted.
        :param filter: Optional filter for documents to be deleted.
        :param delete_all: Flag to indicate if all documents should be deleted.
        :return: True if deletion was successful, False otherwise.
        """
        # Delete from Weaviate
        weaviate_result = await self.weaviate_store.delete(ids, filter, delete_all)

        # Delete from MinIO
        if ids:
            for document_id in ids:
                self.minio_store.delete_object(self.minio_store.bucket_name, document_id)

        return weaviate_result  # Note: This can be refined based on how you want to handle partial failures

    async def create_schema_from_bucket(self, bucket_name: str) -> bool:
        """
        Creates a Weaviate schema class based on a given MinIO bucket name.
        :param bucket_name: The name of the MinIO bucket.
        :return: True if the schema is created successfully, False otherwise.
        """
        # Define the schema with additional properties
        schema = {
            "class": bucket_name,
            "properties": [
                {"name": "path", "dataType": ["string"], "description": "Path of the object"},
                {"name": "object_name", "dataType": ["string"], "description": "Name of the object"},
                {"name": "type", "dataType": ["string"], "description": "Type of the object"},
                {"name": "size", "dataType": ["int"], "description": "Size of the object in bytes"},
                # ... Add more properties as needed
            ]
        }
        return self.weaviate_store.create_class(schema)

    async def batch_ingest_from_bucket(self, bucket_name: str) -> List[str]:
        """
        Lists objects from a MinIO bucket and batch ingests them into Weaviate.
        :param bucket_name: The name of the MinIO bucket.
        :return: List of document IDs that were ingested.
        """
        objects_info = self.minio_store.list_objects(bucket_name)
        documents = []

        for obj in objects_info:
            # Here, obj contains information like name, size, etc.
            document = Document(
                id=obj.object_name,
                path=obj.path,  # Construct path from object_name or additional metadata
                object_name=obj.object_name,
                type=obj.type,  # Determine type (e.g., file extension)
                size=obj.size
                # ... Fill other attributes appropriately
            )
            documents.append(document)

        # Batch ingest into Weaviate
        return await self.upsert(documents)

# Example usage
# hybrid_store = HybridDataStore()
# hybrid_store.upsert([Document(...)])
# hybrid_store.create_schema_from_bucket('my-minio-bucket')
# hybrid_store.batch_ingest_from_bucket('my-minio-bucket')