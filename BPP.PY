from dotenv import load_dotenv
import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_openai import AzureChatOpenAI

def main():
    load_dotenv()  # Load environment variables
    st.set_page_config(page_title="Ask PDF")    
    st.header("Ask PDF")

    # Load API key and endpoint securely from environment variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")

    if not api_key or not azure_endpoint:
        st.error("API Key or Endpoint is missing. Please check your .env file.")
        return

    pdf = st.file_uploader("Upload your PDF", type="pdf")
    
    if pdf:
        pdf_read = PdfReader(pdf)
        text = ""
        for page in pdf_read.pages:  # Accessing pages attribute for iteration
            text += page.extract_text()
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
        chunks = text_splitter.split_text(text)

        embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-3-large",
            azure_endpoint=azure_endpoint,  # Loaded from env variable
            api_key=api_key,  # Loaded from env variable
            openai_api_version=api_version  # Make sure this matches the supported version
        )

        llm = AzureChatOpenAI(
            azure_endpoint=azure_endpoint, 
            api_key=api_key, 
            openai_api_version=api_version
        )

        knowledge_base = FAISS.from_texts(chunks, embeddings)
        userq = st.text_input("Ask your Question...")

        if userq: 
            most_probable_chunk = knowledge_base.similarity_search(userq)
            if most_probable_chunk:
                chain = load_qa_chain(llm, chain_type="stuff")
                res = chain.run(input_documents=most_probable_chunk, question=userq)
                st.write(res)
            else:
                st.write("No relevant chunk found for your question.")
        else:
            st.write("Please enter a question.")

if __name__ == '__main__':
    main()
