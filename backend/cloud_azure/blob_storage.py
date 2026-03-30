from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv
load_dotenv()

class BlobStorageService:

    def __init__(self):
        connection_string = os.getenv("BLOB_CONNECTION_STRING")

        self.container_name = "pdf-documents"

        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string )

        self.container_client = self.blob_service_client.get_container_client(
            self.container_name )

    def upload_pdf(self, file_bytes,blob_name):


        blob_client = self.container_client.get_blob_client(blob_name)

        blob_client.upload_blob(
            data=file_bytes,
            overwrite=True
        )

        return blob_client.url
    
    def download_pdf(self, blob_name):

        blob_client = self.container_client.get_blob_client(blob_name)

        blob_data = blob_client.download_blob().readall()

        return blob_data