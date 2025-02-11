import streamlit as st
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# Streamlit setup
st.header('Legal Advocacy Finder - Document Search')

# User input query
user_input = st.text_input('Enter your legal query here:', 'What is the legal process for contract formation?')

# Azure Search setup
service_name = "your-search-service-name"  # Replace with your actual service name
api_key = "your-api-key"  # Replace with your actual API key
index_name = "your-index-name"  # Replace with the index name you used

# Initialize Azure Search client
azure_credential = AzureKeyCredential(api_key)
search_client = SearchClient(endpoint=f"https://{service_name}.search.windows.net/", index_name=index_name, credential=azure_credential)

KB_FIELDS_CONTENT = "content"
KB_FIELDS_CATEGORY = "category"
KB_FIELDS_SOURCEPAGE = "sourcepage"

# Function to create the prompt for Azure OpenAI (if needed)
def create_prompt(content, query):
    return f"Answer the query: '{query}' based on the following context:\n\n{content}"

# Function to generate the answer using Azure OpenAI (if needed)
def generate_answer(conversation):
    # You would implement the logic to generate a response using Azure OpenAI here
    pass

# Search execution and display of results
if st.button('Submit'):
    # Perform semantic search on Azure Cognitive Search
    results = search_client.search(user_input, query_type="semantic", query_language="en-us", query_speller="lexicon", semantic_configuration_name="default", top=3)
    
    # Display the results
    results_content = [f"{doc[KB_FIELDS_SOURCEPAGE]}: {doc[KB_FIELDS_CONTENT]}" for doc in results]
    content = "\n".join(results_content)
    
    # Display references
    references = [result.split(":")[0] for result in results_content]
    st.markdown("### References:")
    st.write(", ".join(set(references)))

    # Optionally: Generate an AI-based answer using Azure OpenAI
    # You can call the OpenAI API here if integrated
    prompt = create_prompt(content, user_input)
    st.markdown("### Generated Answer:")
    # answer = generate_answer([{"role": "system", "content": "Assistant is a great language model."}, {"role": "user", "content": user_input}])
    st.write("Answer based on Azure OpenAI here")
