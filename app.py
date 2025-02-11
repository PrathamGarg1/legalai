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
    load_dotenv()
    st.set_page_config(page_title="Ask PDF")    
    st.header("Ask PDF")

    pdf = st.file_uploader("Upload your PDF", type="pdf")
    
    if pdf:
        pdf_read = PdfReader(pdf)
        text = ""
        for page in pdf_read.pages:  # Accessing pages attribute for iteration
            text += page.extract_text()
        text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len)
        chunks = text_splitter.split_text(text)

        # embeddings = AzureOpenAIEmbeddings(
        #     model="",
        #     # dimensions: Optional[int] = None, # Can specify dimensions with new text-embedding-3 models
        #     # azure_endpoint="https://<your-endpoint>.openai.azure.com/", If not provided, will read env variable AZURE_OPENAI_ENDPOINT
        #     # api_key=... # Can provide an API key directly. If missing read env variable AZURE_OPENAI_API_KEY
        #     # openai_api_version=..., # If not provided, will read env variable AZURE_OPENAI_API_VERSION
        # )
        embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large")


        llm = AzureChatOpenAI()

        knowledge_base=FAISS.from_texts(chunks,embeddings);
        userq=st.text_input("Ask your Question...")
        if userq: 
            most_probable_chunk=knowledge_base.similarity_search(userq)
            if most_probable_chunk:
                chain=load_qa_chain(llm,chain_type="stuff")
                res = chain.run(input_documents=most_probable_chunk,question=userq)
                st.write(res)
            else:
                st.write("No relevant chunk found for your question.")
        else:
            st.write("Please enter a question.")
if __name__ == '__main__':
    main()

