
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

# Azure Search Service Credentials
service_name = ""  # Your Azure Search service name
searchkey = ""  # Your actual API key
index_name = ""  # Your desired index name

# Construct the Azure Search endpoint
endpoint = f"https://{service_name}.search.windows.net/"

# Initialize Search Client
search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=AzureKeyCredential(searchkey))

# Azure Blob Storage Credentials
account_name = ""  # Your Blob storage account name
sas_token = ""  # Paste your SAS token here
container_name = ""  # Your container name

# Construct the Blob Service URL with SAS Token
blob_service_url = f"https://{account_name}.blob.core.windows.net/?{sas_token}"

# Initialize Blob Service Client with SAS token
blob_service_client = BlobServiceClient(account_url=blob_service_url)
container_client = blob_service_client.get_container_client(container_name)

# Read each file from blob storage and index it
import re

# Read each file from blob storage and index it
def index_text_files():
    for blob in container_client.list_blobs():
        blob_client = container_client.get_blob_client(blob)
        text = blob_client.download_blob().readall().decode("utf-8")

        # Sanitize the blob name to create a valid document ID
        sanitized_id = re.sub(r'[^a-zA-Z0-9-_]', '_', blob.name)

        # Ensure the sanitized ID does not start with an underscore
        if sanitized_id.startswith('_'):
            sanitized_id = 'a' + sanitized_id  # Prepend a valid character

        # Index each file
        document = {
            "id": sanitized_id,  # Use sanitized ID
            "content": text,
            "category": "text",
            "sourcepage": blob.name
        }
        search_client.upload_documents(documents=[document])



# Call the function to index the text files
index_text_files()