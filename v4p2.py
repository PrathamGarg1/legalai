import streamlit as st
import numpy as np
from langchain.vectorstores import FAISS
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

def load_embeddings_from_cosmos():
    items = container.query_items(
        query="SELECT c.id, c.embedding, c.content FROM c",
        enable_cross_partition_query=True
    )
    return list(items)

def create_faiss_index(embeddings_data):
    if not embeddings_data:
        st.error("No embeddings found in the database.")
        return None

    try:
        # Extract vectors and create documents
        vectors = [item['embedding'] for item in embeddings_data]
        texts = [item['content'] for item in embeddings_data]
        
        # Convert to numpy array and check shape
        vectors_np = np.array(vectors, dtype=np.float32)
        st.write(f"Shape of vectors: {vectors_np.shape}")
        
        # Create text_embeddings list
        text_embeddings = list(zip(texts, vectors))
        
        # Create FAISS index
        vector_store = FAISS.from_embeddings(
            text_embeddings=text_embeddings,
            embedding=vectors_np,
            metadatas=[{"id": item['id']} for item in embeddings_data]
        )
        
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
embeddings_data = load_embeddings_from_cosmos()
st.write(f"Loaded {len(embeddings_data)} documents from Cosmos DB")

vector_store = create_faiss_index(embeddings_data)

if vector_store is not None:
    rag_pipeline = setup_rag_pipeline(vector_store)
    
    question = st.text_input("What legal question would you like to analyze?")
    
    if st.button("Analyze"):
        if question:
            with st.spinner("Analyzing..."):
                response = rag_pipeline.invoke({"query": question})
                
                st.write("### Analysis")
                st.write(response["result"])
                
                st.write("### Source Documents")
                for doc in response["source_documents"]:
                    with st.expander(f"Source: {doc.metadata.get('id', 'Unknown')}"):
                        st.write(doc.page_content)
        else:
            st.warning("Please enter a question to analyze.")
else:
    st.error("Could not initialize the system. Please check the logs above for details.")