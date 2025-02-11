# # # import streamlit as st

# # # st.header('Search Engine - Document')

# # # user_input = st.text_input('Enter your question here:', 'What is Diploblastic and Triploblastic Organisation ?')

# # # if st.button('Submit'):

# # #     # Azure Search setup
# # #     service_name = "YOUR-SEARCH-SERVICE-NAME"
# # #     key = "YOUR-SEARCH-SERVICE-ADMIN-API-KEY"
# # #     endpoint = f"https://{service_name}.search.windows.net/"
# # #     index_name = "your-index-name"

# # #     azure_credential = AzureKeyCredential(key)
# # #     search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=azure_credential)

# # #     KB_FIELDS_CONTENT = "content"
# # #     KB_FIELDS_CATEGORY = "category"
# # #     KB_FIELDS_SOURCEPAGE = "sourcepage"

# # #     # Search in the index
# # #     results = search_client.search(user_input, query_type=QueryType.SEMANTIC, query_language="en-us",
# # #                                    query_speller="lexicon", semantic_configuration_name="default", top=3)
    
# # #     results_content = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT] for doc in results]
# # #     content = "\n".join(results_content)
    
# # #     # Display references
# # #     references = [result.split(":")[0] for result in results_content]
# # #     st.markdown("### References:")
# # #     st.write(", ".join(set(references)))

# # #     # Use Azure OpenAI to generate an answer
# # #     conversation = [{"role": "system", "content": "Assistant is a great language model formed by OpenAI."}]
# # #     prompt = create_prompt(content, user_input)
# # #     conversation.append({"role": "assistant", "content": prompt})
# # #     conversation.append({"role": "user", "content": user_input})
# # #     reply = generate_answer(conversation)

# # #     st.markdown("### Answer is:")
# # #     st.write(reply)

# # import streamlit as st
# # import requests
# # import json
# # from azure.core.credentials import AzureKeyCredential
# # from azure.search.documents import SearchClient
# # from azure.search.documents.models import QueryType

# # # Function to generate the prompt for the GPT-3.5 model
# # def create_prompt(content, user_input):
# #     return f"""
# #     Analyze the following legal query based on the retrieved content:
    
# #     Query: {user_input}
    
# #     Content: {content}
    
# #     Provide a detailed analysis including the following points:
# #     1. Identify the primary legal issues
# #     2. Cite relevant sections of law and precedents
# #     3. Analyze potential arguments and counter-arguments
# #     4. Suggest a strategic approach
# #     5. Highlight potential challenges or weaknesses

# #     Format the output as follows:
# #     1. Summary (2-3 sentences)
# #     2. Legal Issues (bullet points)
# #     3. Relevant Laws & Precedents (with citations)
# #     4. Arguments & Counter-Arguments
# #     5. Strategic Recommendations
# #     6. Potential Challenges
# #     """

# # # Function to call OpenAI's API and get the response
# # def generate_answer(conversation):
# #     api_key = "YOUR-OPENAI-API-KEY"
# #     url = "https://api.openai.com/v1/chat/completions"
# #     headers = {
# #         "Content-Type": "application/json",
# #         "Authorization": f"Bearer {api_key}"
# #     }
    
# #     data = {
# #         "model": "gpt-3.5-turbo",
# #         "messages": conversation,
# #         "max_tokens": 1000,
# #         "temperature": 0.5,
# #     }
    
# #     response = requests.post(url, headers=headers, data=json.dumps(data))
    
# #     if response.status_code == 200:
# #         return response.json()['choices'][0]['message']['content']
# #     else:
# #         return f"Error: {response.status_code}, {response.text}"

# # # Streamlit UI setup
# # st.header('Legal Search Engine')

# # user_input = st.text_input('Enter your legal question here:', 'What is Diploblastic and Triploblastic Organisation?')

# # if st.button('Submit'):
# #     # Azure Search setup
# #     service_name = "servicenam"
# #     key = ""
# #     endpoint = f"https://{service_name}.search.windows.net/"
# #     index_name = "indexnam"

# #     azure_credential = AzureKeyCredential(key)
# #     search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=azure_credential)

# #     KB_FIELDS_CONTENT = "content"
# #     KB_FIELDS_CATEGORY = "category"
# #     KB_FIELDS_SOURCEPAGE = "sourcepage"

# #     # Search in the index
# #     results = search_client.search(
# #         user_input, 
# #         query_type=QueryType.SEMANTIC, 
# #         query_language="en-us",
# #         query_speller="lexicon", 
# #         semantic_configuration_name="default", 
# #         top=3
# #     )
    
# #     results_content = [f"{doc[KB_FIELDS_SOURCEPAGE]}: {doc[KB_FIELDS_CONTENT]}" for doc in results]
# #     content = "\n".join(results_content)
    
# #     # Display references
# #     references = [result.split(":")[0] for result in results_content]
# #     st.markdown("### References:")
# #     st.write(", ".join(set(references)))

# #     # Use Azure OpenAI to generate an answer
# #     conversation = [{"role": "system", "content": "You are a legal assistant."}]
# #     prompt = create_prompt(content, user_input)
# #     conversation.append({"role": "user", "content": prompt})
# #     reply = generate_answer(conversation)

# #     st.markdown("### Analysis:")
# #     st.write(reply)

# import streamlit as st
# from azure.search.documents import SearchClient
# from azure.core.credentials import AzureKeyCredential
# import requests
# import json

# # Streamlit header
# st.header('Legal Document Analysis Tool')

# # User input
# user_input = st.text_input('Enter your legal query:', 'Example: I want to defend my client Raman who is accused of murder.')

# if st.button('Submit'):
#     # Azure Search setup
#     service_name = "servicenam"  # Replace with your Azure Search service name
#     key = ""  # Replace with your Azure Search key
#     endpoint = f"https://{service_name}.search.windows.net/"
#     index_name = "finalindex"  # Replace with your Azure Search index name
#     azure_credential = AzureKeyCredential(key)
#     search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=azure_credential)

#     KB_FIELDS_CONTENT = "content"
#     KB_FIELDS_SOURCEPAGE = "sourcepage"

#     # Semantic Search query in Azure Search
#     results = search_client.search(
#         user_input,
#         query_type="semantic",  # Use semantic search
#         semantic_configuration_name="default",  # Semantic configuration must match the index setup
#         top=3
#     )

#     results_content = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT] for doc in results]
#     content = "\n".join(results_content)

#     # Display references
#     references = [result.split(":")[0] for result in results_content]
#     st.markdown("### References:")
#     st.write(", ".join(set(references)))

#     # Azure OpenAI setup (optional)
#     azure_openai_endpoint = "https://testsaas.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2023-03-15-preview"
#     openai_key = ""  # Replace with your Azure OpenAI key

#     # Create prompt for Azure OpenAI
#     def create_prompt(content, user_query):
#         return (
#             f"Based on the following legal documents:\n\n{content}\n\n"
#             f"Please analyze the query: '{user_query}' and provide detailed insights as follows:\n"
#             "1. Summary (2-3 sentences)\n"
#             "2. Legal Issues (bullet points)\n"
#             "3. Relevant Laws & Precedents (with citations)\n"
#             "4. Arguments & Counter-Arguments\n"
#             "5. Strategic Recommendations\n"
#             "6. Potential Challenges\n"
#         )

#     # Generate answer from Azure OpenAI (optional)
#     def generate_answer(prompt):
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {openai_key}",
#         }
#         data = {
#             "messages": [{"role": "user", "content": prompt}],
#             "max_tokens": 500,
#             "temperature": 0.7,
#         }

#         response = requests.post(azure_openai_endpoint, headers=headers, json=data)
#         if response.status_code == 200:
#             answer = response.json()
#             return answer['choices'][0]['message']['content']
#         else:
#             st.error(f"Error: {response.status_code} - {response.text}")
#             return "An error occurred while generating the response."

#     # Use Azure OpenAI to generate analysis (optional)
#     prompt = create_prompt(content, user_input)
#     result = generate_answer(prompt)

#     # Display generated result
#     st.markdown("### Result:")
#     st.write(result)
import streamlit as st
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import requests
import json

# Streamlit header
st.header('Legal Document Analysis Tool')

# User input
user_input = st.text_input('Enter your question here:', 'I want to defend my client Raman who is accused of murder at Verka Chowk')

if st.button('Submit'):
    # Azure Search setup
    service_name = "servicenam"  # Replace with your Azure Search service name
    key = ""  # Replace with your Azure Search key
    endpoint = f"https://{service_name}.search.windows.net/"
    index_name = "indexnam"  # Replace with your Azure Search index name
    azure_credential = AzureKeyCredential(key)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=azure_credential)

    KB_FIELDS_CONTENT = "content"
    KB_FIELDS_SOURCEPAGE = "sourcepage"

    # Search in the index (removed semantic configuration)
    results = search_client.search(
        user_input,
        query_type="simple",  # Changed to simple query since semantic search requires a configuration
        top=3
    )

    results_content = [doc[KB_FIELDS_SOURCEPAGE] + ": " + doc[KB_FIELDS_CONTENT] for doc in results]
    content = "\n".join(results_content)

    # Display references
    references = [result.split(":")[0] for result in results_content]
    st.markdown("### References:")
    st.write(", ".join(set(references)))

    # Azure OpenAI setup
    azure_openai_endpoint = ""
    openai_key = ""  # Replace with your Azure OpenAI key

    # Create prompt for Azure OpenAI
    def create_prompt(content, user_query):
        return (
            f"Based on the following legal documents:\n\n{content}\n\n"
            f"Please analyze the query: '{user_query}' and provide detailed insights as follows:\n"
            "1. Summary (2-3 sentences)\n"
            "2. Legal Issues (bullet points)\n"
            "3. Relevant Laws & Precedents (with citations)\n"
            "4. Arguments & Counter-Arguments\n"
            "5. Strategic Recommendations\n"
            "6. Potential Challenges\n"
        )

    # Generate answer from Azure OpenAI
    def generate_answer(prompt):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_key}",
        }
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.7,
        }

        response = requests.post(azure_openai_endpoint, headers=headers, json=data)
        if response.status_code == 200:
            answer = response.json()
            return answer['choices'][0]['message']['content']
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return "An error occurred while generating the response."

    # Use Azure OpenAI to generate an answer
    prompt = create_prompt(content, user_input)
    reply = generate_answer(prompt)

    st.markdown("### Answer:")
    st.write(reply)
