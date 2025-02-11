from azure.storage.blob import BlobServiceClient 
import os
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document  # Importing Document from LangChain
import requests
import time
import json
from azure.cosmos import CosmosClient, PartitionKey

# Azure Blob Storage Credentials
account_name = "stprathamgar189078971507"
sas_token = ""
container_name = ""

# Initialize Blob Service Client with SAS token
blob_service_url = f"https://{account_name}.blob.core.windows.net/?{sas_token}"
blob_service_client = BlobServiceClient(account_url=blob_service_url)

# Function to read judgments from Azure Blob Storage
def get_judgments_from_blob(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs()

    judgments = []
    for blob in blobs:
        blob_client = container_client.get_blob_client(blob)
        judgment_text = blob_client.download_blob().readall().decode('utf-8')
        judgments.append(judgment_text)
    
    # Debugging: Print out how many judgments were retrieved
    print(f"Retrieved {len(judgments)} judgments from Blob storage.")
    
    # Debugging: Check if judgments list is empty
    if not judgments:
        print("No judgments were found in the blob storage.")
    
    return judgments

# Custom Azure OpenAI Embedding function
class AzureOpenAIEmbeddings:
    def __init__(self, endpoint, api_key, batch_size=50, delay=60):
        self.endpoint = endpoint
        self.api_key = api_key
        self.batch_size = batch_size  # Number of documents to send in each request
        self.delay = delay  # Delay between batches to avoid hitting rate limits

    def embed_documents(self, documents):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        all_embeddings = []
        for i in range(0, len(documents), self.batch_size):
            batch = documents[i:i + self.batch_size]
            data = {
                "input": [doc.page_content for doc in batch]
            }

            response = requests.post(self.endpoint, json=data, headers=headers)
            if response.status_code == 429:
                # Handle rate limit, sleep and retry
                print(f"Rate limit hit, sleeping for {self.delay} seconds...")
                time.sleep(self.delay)
                continue  # Retry the current batch after the delay
            elif response.status_code != 200:
                raise Exception(f"Error with embedding request: {response.text}")
            
            embeddings = response.json()["data"]
            all_embeddings.extend([embedding["embedding"] for embedding in embeddings])

            # Debugging: Show progress
            print(f"Processed batch {i // self.batch_size + 1}/{(len(documents) + self.batch_size - 1) // self.batch_size}")

            # Delay between batches to avoid exceeding rate limits
            time.sleep(self.delay)

        # Debugging: Print number of embeddings created
        print(f"Generated {len(all_embeddings)} embeddings.")

        return all_embeddings

# Create the vector database using Azure OpenAI Embeddings and store in Cosmos DB
def create_vector_database_and_store_in_cosmos(judgments, endpoint, api_key, cosmos_endpoint, cosmos_key, database_name, container_name, limit=None):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = [Document(page_content=judgment) for judgment in judgments]

    if documents:
        print(f"First document: {documents[0].page_content[:500]}...")
    else:
        print("No judgments were passed to the splitter.")
        return

    split_docs = splitter.split_documents(documents)
    
    # If limit is set, process only that many split docs for testing
    if limit:
        split_docs = split_docs[:limit]
    
    print(f"Split documents into {len(split_docs)} chunks for testing.")
    
    embedding_model = AzureOpenAIEmbeddings(endpoint, api_key)
    embeddings = embedding_model.embed_documents(split_docs)

    cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
    database = cosmos_client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    for i, (embedding, document) in enumerate(zip(embeddings, split_docs)):
        item = {
            "id": str(i),
            "embedding": embedding,
            "content": document.page_content
        }
        container.upsert_item(item)
        print(f"Upserted item {i} into Cosmos DB.")

# Your Azure OpenAI embedding endpoint and API key
embedding_endpoint = "https://testsaas.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"
api_key = ""

# Azure Cosmos DB credentials
cosmos_endpoint = "https://cosmosrgeastus7b6a2803-7e3b-4c35-9a4cdb.documents.azure.com:443/"
cosmos_key = "=="
database_name = "databaseid"
cosmos_container_name = "containerid"

# Judgments loaded from Blob Storage
judgments = get_judgments_from_blob(container_name)
if judgments:
    create_vector_database_and_store_in_cosmos(judgments, embedding_endpoint, api_key, cosmos_endpoint, cosmos_key, database_name, cosmos_container_name, limit=10)
else:
    raise Exception("No judgments were retrieved from the Blob storage.")
