from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SimpleField, SearchableField, SearchIndex
from azure.core.credentials import AzureKeyCredential

# Replace these with your actual service details
service_name = ""  # Replace with your search service name
api_key = ""  # Replace with your actual API key
index_name = "indexnam"  # Replace with the desired index name

# Construct the endpoint based on the service name
endpoint = f"https://{service_name}.search.windows.net/"

# Set up the Azure credentials using the API key
azure_credential = AzureKeyCredential(api_key)

# Set up SearchIndexClient
index_client = SearchIndexClient(endpoint=endpoint, credential=azure_credential)

# Define the index schema
fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft"),
    SimpleField(name="category", type="Edm.String"),
    SimpleField(name="sourcepage", type="Edm.String")
]

index = SearchIndex(name=index_name, fields=fields)

# Create the index
index_client.create_index(index)