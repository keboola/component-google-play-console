import os
import json

from pathlib import Path

from google.cloud import storage
from google.oauth2 import service_account


class CloudStorageClient:
    def __init__(self, service_account_key: str) -> None:
        self.credentials = service_account.Credentials.from_service_account_info(json.loads(service_account_key))
        self.client = storage.Client(credentials=self.credentials)

    def download_files_from_bucket(self, bucket_name: str, destination_folder: str):
        os.makedirs(destination_folder, exist_ok=True)

        bucket = self.client.bucket(bucket_name)
        blobs = bucket.list_blobs()

        for blob in blobs:
            if blob.name.endswith("/"):
                continue

            relative_path = blob.name

            destination_path = Path(destination_folder) / relative_path

            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            blob.download_to_filename(destination_path)
