import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Blob Storage and Load Judgments
st.title("Judgment Search Assistant")
container_name = "your-container-name"
judgments = get_judgments_from_blob(container_name)

# Create Vector Database
vector_store = create_vector_database(judgments)

# Initialize RAG System
qa_system = setup_rag_pipeline(vector_store)

# Streamlit Interface for Querying the Model
question = st.text_input("Ask a question about the judgments:")

if st.button("Submit"):
    if question:
        response = qa_system.invoke({"query": question})
        st.write("**Response:**")
        st.write(response["result"])
        st.write("**Source Judgments:**")
        for doc in response["source_documents"]:
            st.write(doc.page_content)
    else:
        st.write("Please enter a question.")
