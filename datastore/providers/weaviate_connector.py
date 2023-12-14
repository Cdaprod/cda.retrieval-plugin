from pydantic import BaseModel, Field
from typing import List, Optional
from dataclasses import dataclass

# Define Pydantic models for input and output data structures

class DocumentMetadata(BaseModel):
    document_id: str
    source: Optional[str]
    source_id: Optional[str]
    url: Optional[str]
    created_at: Optional[str]
    author: Optional[str]

class DocumentChunk(BaseModel):
    chunk_id: str
    text: str
    metadata: DocumentMetadata

class QueryWithEmbedding(BaseModel):
    query: str
    embedding: List[float]
    top_k: Optional[int] = 10
    filter: Optional[DocumentMetadata] = None

class DocumentChunkWithScore(BaseModel):
    id: str
    text: str
    score: float
    metadata: DocumentMetadata

class QueryResult(BaseModel):
    query: str
    results: List[DocumentChunkWithScore]

# Data class for the actual data
@dataclass
class DocumentData:
    chunk_id: str
    document_id: str
    text: str
    source: Optional[str]
    source_id: Optional[str]
    url: Optional[str]
    created_at: Optional[str]
    author: Optional[str]
    embedding: List[float]

# Other necessary models and data classes as required by the functions in weaviate_datastore.py
