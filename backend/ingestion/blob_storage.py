import os
from azure.storage.blob import BlobServiceClient
from backend.config import AZURE_STORAGE_CONNECTION_STRING,AZURE_STORAGE_CONTAINER


def upload_pdf(file_path:str):
    blob_service_client=BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    blob_name=os.path.basename(file_path)

    blob_client=blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER,blob=blob_name)

    with open(file_path,"rb") as data:
        blob_client.upload_blob(data,overwrite=True)

    return blob_client.url

url = upload_pdf("backend/ingestion/attention-is-all-you-need-Paper.pdf")
print(url)


