from azure.storage.blob import BlobServiceClient
import os
import requests
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import AzureChatOpenAI

# Azure Blob Storage Credentials
account_name = ""  # Your Blob storage account name
sas_token = ""
container_name = ""  # Your container name

# Construct the Blob Service URL with SAS Token
blob_service_url = f"https://{account_name}.blob.core.windows.net/?{sas_token}"

# Initialize Blob Service Client with SAS token
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
    
    return judgments

# Custom Azure OpenAI Embedding function
class AzureOpenAIEmbeddings:
    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.api_key = api_key

    def embed_documents(self, documents):
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key
        }

        # Pass the list of strings directly as data
        data = documents  # Ensure this is a list of strings

        response = requests.post(self.endpoint, json=data, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Error with embedding request: {response.text}")
        
        # Extract the embeddings from the response
        embeddings = response.json()["data"]
        return [embedding["embedding"] for embedding in embeddings]

# Create the vector database using Azure OpenAI Embeddings
def create_vector_database(judgments, endpoint, api_key):
    # Split documents into chunks for better retrieval
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = splitter.split_documents([{"content": judgment} for judgment in judgments])
    
    # Create embeddings using the custom Azure OpenAI embedding class
    embedding_model = AzureOpenAIEmbeddings(endpoint, api_key)
    embeddings = embedding_model.embed_documents([doc['content'] for doc in documents])  # Extracting content directly
    
    # Create FAISS vector store
    faiss_store = FAISS.from_embeddings(embeddings, documents)
    
    return faiss_store

# Your Azure OpenAI embedding endpoint and API key
embedding_endpoint = "https://testsaas.openai.azure.com/openai/deployments/text-embedding-3-large/embeddings?api-version=2023-05-15"
api_key = ""

# Judgments loaded from Blob Storage
# Judgments loaded from Blob Storage
judgments = get_judgments_from_blob(container_name)

# Debug: Check if judgments are loaded correctly
if not judgments:
    raise Exception("No judgments were retrieved from the Blob Storage.")

# Create Vector Database with Azure OpenAI Embeddings
vector_store = create_vector_database(judgments, embedding_endpoint, api_key)

def setup_rag_pipeline(vectorstore):
    # Azure OpenAI Configuration with provided endpoint and key
    llm = AzureChatOpenAI(
        azure_deployment="gpt-35-turbo",  # Deployment name (model identifier)
        azure_endpoint="https://testsaas.openai.azure.com",  # Your specific Azure endpoint
        openai_api_key=api_key,  # Your API key for Azure OpenAI
        api_version="2023-03-15-preview",  # API version
        model="gpt-35-turbo",  # Model name
        temperature=0.3  # Control the creativity of the output (adjustable)
    )

    # Create a Prompt Template
    prompt_template = """You are an AI Assistant. Given the following context:
    {context}
    
    Answer the following question:
    {question}
    
    Assistant:"""
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    # Create the Retrieval QA Chain
    qa = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa

# Setup the RAG pipeline
rag_pipeline = setup_rag_pipeline(vector_store)
