from minio import Minio
from minio.error import S3Error
import os
from dotenv import load_dotenv
from typing import List


class MinioDataStore:
    def __init__(self):
        """
        Initialize a connection to the MinIO server using environment variables.
        """
        load_dotenv()

        self.minio_url = os.getenv('MINIO_URL')
        self.minio_access_key = os.getenv('MINIO_ACCESS_KEY')
        self.minio_secret_key = os.getenv('MINIO_SECRET_KEY')
        self.bucket_name = os.getenv('MINIO_BUCKET_NAME', 'default-bucket')

        if not all([self.minio_url, self.minio_access_key, self.minio_secret_key, self.bucket_name]):
            raise ValueError("Missing MinIO configuration details in environment variables")

        self.client = Minio(
            self.minio_url,
            access_key=self.minio_access_key,
            secret_key=self.minio_secret_key,
            secure=False  # Set to True if using HTTPS
        )

    def upload_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """
        Uploads a file from a local path to a MinIO bucket.
        :param bucket_name: The name of the bucket.
        :param object_name: The object name in the bucket.
        :param file_path: The local file path to be uploaded.
        """
        try:
            self.client.put_object(bucket_name, object_name, file_path)
        except S3Error as e:
            print(f"Error uploading object to MinIO: {e}")

    def download_object(self, bucket_name: str, object_name: str, file_path: str) -> None:
        """
        Downloads an object from a MinIO bucket to a local file path.
        :param bucket_name: The name of the bucket.
        :param object_name: The object name in the bucket.
        :param file_path: The local file path to save the downloaded object.
        """
        try:
            self.client.get_object(bucket_name, object_name, file_path)
        except S3Error as e:
            print(f"Error downloading object from MinIO: {e}")

    def delete_object(self, bucket_name: str, object_name: str) -> None:
        """
        Deletes an object from a MinIO bucket.
        :param bucket_name: The name of the bucket.
        :param object_name: The object name to be deleted.
        """
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as e:
            print(f"Error deleting object from MinIO: {e}")

    def list_objects(self, bucket_name: str) -> List[str]:
        """
        Lists all objects in a specified bucket.
        :param bucket_name: The name of the bucket to list objects from.
        ↩️ A list of object names.
        """
        try:
            objects = self.client.list_objects(bucket_name, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"Error listing objects in bucket {bucket_name}: {e}")
            return []
            
#### Example usage to initialize MinioDataStore class
# minio_store = MinioDataStore()

#### Example usage for individual upload_object download_object delete_object functions
# minio_store.upload_object('my-bucket', 'my-object', '/path/to/myfile')
# minio_store.download_object('my-bucket', 'my-object', '/path/to/download')
# minio_store.delete_object('my-bucket', 'my-object')

#### Example usage to print list of 'object_names'
# object_names = minio_store.list_objects('my-bucket')
# print(object_names)