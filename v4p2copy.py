import streamlit as st
import numpy as np
from langchain.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from langchain.docstore.document import Document
from azure.cosmos import CosmosClient
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_openai import AzureChatOpenAI

# Azure Cosmos DB credentials
cosmos_endpoint = "https://cosmosrgeastus7b6a2803-7e3b-4c35-9a4cdb.documents.azure.com:443/"
cosmos_key = "=="
database_name = "databaseid"
cosmos_container_name = "containerid"

# Azure OpenAI credentials
api_key = ""

# Initialize Cosmos DB Client
cosmos_client = CosmosClient(cosmos_endpoint, cosmos_key)
database = cosmos_client.get_database_client(database_name)
container = database.get_container_client(cosmos_container_name)

class CustomEmbeddings(Embeddings):
    def __init__(self, embeddings_data):
        self.embeddings_dict = {item['content']: item['embedding'] for item in embeddings_data}
    
    def embed_documents(self, texts):
        return [self.embeddings_dict[text] for text in texts if text in self.embeddings_dict]
    
    def embed_query(self, text):
        # Return a zero vector of the same dimension as your embeddings
        return [0.0] * len(next(iter(self.embeddings_dict.values())))

def load_embeddings_from_cosmos():
    try:
        items = container.query_items(
            query="SELECT c.id, c.embedding, c.content FROM c",
            enable_cross_partition_query=True
        )
        return list(items)
    except Exception as e:
        st.error(f"Error loading from Cosmos DB: {str(e)}")
        return []

def create_faiss_index(embeddings_data):
    if not embeddings_data:
        st.error("No embeddings found in the database.")
        return None

    try:
        # Create documents and get embedding dimension
        documents = [
            Document(page_content=item['content'], metadata={"id": item['id']})
            for item in embeddings_data
        ]
        
        # Initialize custom embeddings
        embedding_function = CustomEmbeddings(embeddings_data)
        
        # Create FAISS index
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embedding_function
        )
        
        st.success(f"Successfully created FAISS index with {len(documents)} documents")
        return vector_store
    except Exception as e:
        st.error(f"Error creating FAISS index: {str(e)}")
        return None

def setup_rag_pipeline(vector_store):
    llm = AzureChatOpenAI(
        azure_deployment="gpt-35-turbo",
        azure_endpoint="https://testsaas.openai.azure.com",
        openai_api_key=api_key,
        api_version="2023-03-15-preview",
        temperature=0.3
    )

    prompt_template = """You are an AI Assistant for legal analysis. Given the following context:
    {context}
    
    Please answer this question: {question}
    
    Provide your analysis in the following structure:
    1. Summary (2-3 sentences)
    2. Legal Issues (bullet points)
    3. Relevant Laws & Precedents (with citations)
    4. Analysis
    5. Conclusion
    
    Be specific and cite relevant cases when possible."""
    
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 6}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa

# Streamlit UI
st.title("Legal Document Analysis Assistant")

# Load embeddings and create index
with st.spinner("Loading embeddings from database..."):
    embeddings_data = load_embeddings_from_cosmos()
    st.info(f"Loaded {len(embeddings_data)} documents from Cosmos DB")

    if embeddings_data:
        st.write("Sample embedding dimension:", len(embeddings_data[0]['embedding']))

vector_store = create_faiss_index(embeddings_data)

if vector_store is not None:
    rag_pipeline = setup_rag_pipeline(vector_store)
    
    question = st.text_input("What legal question would you like to analyze?")
    
    if st.button("Analyze"):
        if question:
            with st.spinner("Analyzing..."):
                try:
                    response = rag_pipeline.invoke({"query": question})
                    
                    st.write("### Analysis")
                    st.write(response["result"])
                    
                    st.write("### Source Documents")
                    for doc in response["source_documents"]:
                        with st.expander(f"Source: {doc.metadata.get('id', 'Unknown')}"):
                            st.write(doc.page_content)
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
        else:
            st.warning("Please enter a question to analyze.")
else:
    st.error("Could not initialize the system. Please check the logs above for details.")