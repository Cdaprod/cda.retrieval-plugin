To create a `HybridDataStore` class that integrates with the `DataStore` abstract base class, you would need to implement the abstract methods defined in `DataStore`, such as `_upsert`, `_query`, and `delete`. The `HybridDataStore` should internally manage instances of both Weaviate and MinIO data stores, delegating operations to each based on the type of data being handled.

Here's a basic outline for the `HybridDataStore` class:

```python
from datastore.weaviate_datastore import WeaviateDataStore
from datastore.minio_datastore import MinioDataStore

class HybridDataStore(DataStore):
    def __init__(self):
        self.weaviate_store = WeaviateDataStore()
        self.minio_store = MinioDataStore()

    async def _upsert(self, chunks: Dict[str, List[DocumentChunk]]) -> List[str]:
        # Logic to decide whether to store in Weaviate or MinIO
        # For example, use Weaviate for textual data and MinIO for binary data
        # This is a simplified example; your actual implementation might be more complex
        document_ids = []
        for doc_id, doc_chunks in chunks.items():
            if should_use_weaviate(doc_chunks):
                document_ids.extend(await self.weaviate_store._upsert({doc_id: doc_chunks}))
            else:
                document_ids.extend(await self.minio_store._upsert({doc_id: doc_chunks}))
        return document_ids

    async def _query(self, queries: List[QueryWithEmbedding]) -> List[QueryResult]:
        # Assuming query operations are mainly handled by Weaviate
        return await self.weaviate_store._query(queries)

    async def delete(self, ids: Optional[List[str]] = None, filter: Optional[DocumentMetadataFilter] = None, delete_all: Optional[bool] = None) -> bool:
        # Implement logic to delete data from both Weaviate and MinIO
        weaviate_result = await self.weaviate_store.delete(ids, filter, delete_all)
        minio_result = await self.minio_store.delete(ids, filter, delete_all)
        return weaviate_result and minio_result

# Helper function to decide if data should be stored in Weaviate
def should_use_weaviate(doc_chunks: List[DocumentChunk]) -> bool:
    # Implement your logic here
    # For example, check the type of data in doc_chunks or its size
    return True
```

### Key Points:
- **Delegation of Responsibilities**: The `HybridDataStore` should intelligently delegate tasks to either the Weaviate or MinIO datastore based on the nature of the data or specific criteria you define.
- **Maintaining Consistency**: Ensure that operations across both datastores remain consistent. For instance, if an operation fails in one, you might need to roll back changes in the other.
- **Performance Considerations**: The hybrid approach might introduce complexity in data management. Optimize for performance where necessary.
- **Error Handling**: Robust error handling is crucial, especially when dealing with two different data storage systems.

This is a simplified example. Your actual implementation will depend on the specifics of how you want to handle different types of data and the operations you need to support. You'll also need to ensure that the integration aligns with the overall architecture of your application.

Given your data flow where data always originates from a raw bucket in MinIO and is then processed and written to a 'cleaned' Weaviate bucket, the `HybridDataStore` should be designed to facilitate this workflow efficiently. Here’s how you can implement this process:

### 1. Data Ingestion from Raw Bucket
- The `HybridDataStore` should first interact with the MinIO store to retrieve raw data.
- Implement a method in `MinioDataStore` to fetch data from the specified raw bucket.

### 2. Data Processing and Cleaning
- Once raw data is fetched, it should be processed and cleaned according to your requirements. This step typically involves data transformation, normalization, and cleaning.
- This processing might be done within the `HybridDataStore` or through a separate service or function, depending on the complexity of your data processing logic.

### 3. Storing Processed Data in Weaviate
- After processing the data, `HybridDataStore` should use the `WeaviateDataStore` to store the cleaned data in Weaviate.
- Ensure that the data structure aligns with what Weaviate expects, including any necessary metadata.

### 4. Updating the HybridDataStore Class
- Modify the `_upsert` method in `HybridDataStore` to implement this workflow. It should fetch data from the MinIO raw bucket, process it, and then store the cleaned data in Weaviate.
- Similarly, for the `query` and `delete` methods, you might predominantly interact with the Weaviate datastore, as MinIO is primarily used for raw data storage in this workflow.

### Example Implementation:

```python
class HybridDataStore(DataStore):
    # ... other methods ...

    async def _upsert(self, documents: List[Document]) -> List[str]:
        # Fetch data from the raw MinIO bucket
        raw_data = await self.minio_store.fetch_from_bucket(raw_bucket_name)

        # Process and clean the data
        cleaned_data = process_data(raw_data)  # Define process_data function as per your requirements

        # Store the cleaned data in Weaviate
        cleaned_document_chunks = get_document_chunks(cleaned_data, chunk_token_size)
        return await self.weaviate_store._upsert(cleaned_document_chunks)

    # ... implementation for _query and delete ...
```

In this example, `fetch_from_bucket` and `process_data` are hypothetical functions you would need to implement based on your specific data processing logic.

### Key Considerations:
- **Efficient Data Handling**: Optimize data transfer and processing to handle large datasets effectively.
- **Error Handling**: Implement robust error handling, especially for the data transformation and cleaning phase.
- **Modularity**: Keep the data processing logic modular for easy maintenance and potential scaling or changes in the workflow.

This approach ensures a clear separation of concerns, with MinIO handling raw data and Weaviate managing the cleaned, processed data. The `HybridDataStore` acts as the orchestrator of this workflow, ensuring smooth data transitions between the two systems.

# Extending the functionality of HybridDataStore()

Expanding on the Weaviate schema to include additional properties from the MinIO bucket objects, such as path, object name, type, size, etc., can be done within the `HybridDataStore` class. Here's how you can modify the `create_schema_from_bucket` and `batch_ingest_from_bucket` methods:

### Modified HybridDataStore Class:

```python
# ... [Previous Imports and Code] ...

class HybridDataStore:
    # ... [Other methods] ...

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
# hybrid_store.create_schema_from_bucket('my-minio-bucket')
# hybrid_store.batch_ingest_from_bucket('my-minio-bucket')
```

### Explanation:
- **Schema Enhancement**: The schema now includes properties like `path`, `object_name`, `type`, and `size`. You may need to adapt these properties based on the actual data structure and metadata available from MinIO objects.
- **Ingestion Logic**: In `batch_ingest_from_bucket`, the method retrieves additional information from each object in the MinIO bucket and populates the respective fields in the Weaviate schema.

### Considerations:
- **Object Metadata**: Ensure that the MinIO SDK's `list_objects` method or equivalent provides the necessary metadata for these additional properties.
- **Data Mapping**: You may need to process or transform the object metadata from MinIO to fit into the Weaviate schema correctly, especially for fields like `type` or `path`.