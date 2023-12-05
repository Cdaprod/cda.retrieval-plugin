import os
from langchain.tools import BaseTool, Tool
from minio import Minio
from pydantic import BaseModel, Field
from typing import Optional
import tempfile
from langchain.callbacks.manager import CallbackManagerForToolRun, AsyncCallbackManagerForToolRun

# Get Minio Client credentials from environment variables
minio_server = os.getenv('MINIO_SERVER')
minio_access_key = os.getenv('MINIO_ACCESS_KEY')
minio_secret_key = os.getenv('MINIO_SECRET_KEY')

# Initialize Minio Client
minioClient = Minio(
    minio_server,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=False  # Set True if your Minio server uses TLS
)

# Define the input schema for Minio operations
class MinioInput(BaseModel):
    bucket_name: str = Field(description="The name of the bucket")
    object_name: str = Field(description="The object name in the bucket")
    file_path: Optional[str] = Field(description="The local file path for upload/download operations")

# Create a Minio tool using the BaseTool subclassing approach
class MinioTool(BaseTool):
    name = "MinioTool"
    description = "A tool for interacting with a Minio S3 bucket."
    args_schema = MinioInput

    def _run(
        self,
        bucket_name: str,
        object_name: str,
        file_path: Optional[str] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool to upload or fetch objects from Minio."""
        with tempfile.TemporaryDirectory() as temp_dir_name:
            if file_path:  # Assume an upload operation if file_path is provided
                minioClient.put_object(bucket_name, object_name, file_path)
                return f"File {file_path} uploaded to {bucket_name}/{object_name}"
            else:  # Assume a fetch operation if file_path is not provided
                result_file_path = os.path.join(temp_dir_name, object_name)
                minioClient.get_object(bucket_name, object_name, result_file_path)
                return f"File {bucket_name}/{object_name} downloaded to {result_file_path}"

    async def _arun(
        self,
        bucket_name: str,
        object_name: str,
        file_path: Optional[str] = None,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        # The async version of the operations could be implemented here
        raise NotImplementedError("Async operations are not supported yet")

# Now you can add MinioTool to your list of tools when initializing the agent.
tools = [MinioTool(), ...]  # Other tools
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# Run the agent with a task involving the Minio tool
response = agent.run(
    "Upload a file to my Minio bucket",
    # Provide necessary input for the Minio tool
    {
        "bucket_name": "media",
        "object_name": "content/woodworking/photo.jpg",
        "file_path": "/path/to/local/photo.jpg"
    }
)

print(response)  # Check the result of the Minio tool operation