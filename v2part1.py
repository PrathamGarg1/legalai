from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SimpleField, SearchableField, SearchIndex, SemanticConfiguration, SemanticField, PrioritizedFields, SemanticSettings
from azure.core.credentials import AzureKeyCredential

# Replace these with your actual service details
service_name = "servicenam"  # Replace with your search service name
api_key = ""  # Replace with your actual API key
index_name = "v2index"  # Replace with the desired index name

# Construct the endpoint based on the service name
endpoint = f"https://{service_name}.search.windows.net/"

# Set up the Azure credentials using the API key
azure_credential = AzureKeyCredential(api_key)

# Set up SearchIndexClient
index_client = SearchIndexClient(endpoint=endpoint, credential=azure_credential)

# Define the index schema
fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="content", type="Edm.String", analyzer_name="en.microsoft"),  # Main content
    SimpleField(name="category", type="Edm.String"),  # Document category
    SimpleField(name="sourcepage", type="Edm.String")  # Original source
]

# Define semantic configuration for better ranking
semantic_config = SemanticConfiguration(
    name="default",
    prioritized_fields=PrioritizedFields(
        title_field=None,
        content_field=SemanticField(field_name="content"),
        keyword_fields=[]
    )
)

# Define the index with semantic settings
index = SearchIndex(
    name=index_name,
    fields=fields,
    semantic_settings=SemanticSettings(configurations=[semantic_config])
)

# Create the index
index_client.create_index(index)
