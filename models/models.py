from pydantic import BaseModel
from typing import Union, List, Optional
from enum import Enum

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class SourceCode(BaseModel):
    id: str = Field(description="Unique identifier for the source code object.")
    imports: List[str] = Field(description="List of extracted required packages.")
    classes: List[str] = Field(description="List of extracted classes from the code.")
    code: str = Field(description="Source code snippets.")
    syntax: str = Field(description="The programming language syntax/extension (e.g., Python).")
    context: str = Field(description="Any extracted text, markdown, comments, or docstrings.")
    metadata: dict = Field(description="Extracted or generated metadata tags for top-level cataloging and code object management.")

class Table(BaseModel):
    id: str = Field(description="Unique identifier for the table object.")
    headers: List[str] = Field(description="Headers of the table")
    rows: List[Dict[str, Any]] = Field(description="Rows of the table, each row being a dictionary")

class MarkdownDocument(BaseModel):
    id: str = Field(description="Unique identifier for the document object.")
    metadata: Dict[str, Any] = Field(description="Metadata of the document")
    tables: List[Table] = Field(description="List of tables in the document")
    code_blocks: List[SourceCode] = Field(description="List of code blocks in the document")
    content: str = Field(description="The textual content of the document")
    blob_data: List[bytes] = Field(description="The image or video content of the document")

class BucketObject(BaseModel):
    id: str = Field(description="Unique identifier for the bucket object.")
    object_name: str
    object_type: Optional[str] = None
    size: Optional[int] = None

class Bucket(BaseModel):
    id: str = Field(description="Unique identifier for the bucket.")
    name: str
    objects: List[BucketObject]
    
# Example usage for Bucket model:
# bucket = Bucket(name="my_bucket", objects=[BucketObject(object_name="file1.txt", object_type="text", size=1024)])

class LangchainTools(BaseModel):
    id: str = Field(description="Unique identifier for the source code object.")
    tool_name: str
    version: str
    metadata: dict

class CodeDocs(BaseModel):
    document_id: str
    content: str
    metadata: dict
    
class Source(str, Enum):
    email = "email"
    file = "file"
    chat = "chat"

class DocumentMetadata(BaseModel):
    source: Optional[Source] = None
    source_id: Optional[str] = None
    url: Optional[str] = None
    created_at: Optional[str] = None
    author: Optional[str] = None

class DocumentChunkMetadata(DocumentMetadata):
    document_id: Optional[str] = None


class DocumentChunk(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: DocumentChunkMetadata
    embedding: Optional[List[float]] = None


class DocumentChunkWithScore(DocumentChunk):
    score: float

class Document(BaseModel):
    id: Optional[str] = None
    text: str
    metadata: Optional[DocumentMetadata] = None

class DocumentWithChunks(Document):
    chunks: List[DocumentChunk]


class DocumentMetadataFilter(BaseModel):
    document_id: Optional[str] = None
    source: Optional[Source] = None
    source_id: Optional[str] = None
    author: Optional[str] = None
    start_date: Optional[str] = None  # any date string format
    end_date: Optional[str] = None  # any date string format


class Query(BaseModel):
    query: str
    filter: Optional[DocumentMetadataFilter] = None
    top_k: Optional[int] = 3


class QueryWithEmbedding(Query):
    embedding: List[float]


class QueryResult(BaseModel):
    query: str
    results: List[DocumentChunkWithScore]
