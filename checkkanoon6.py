from azure.storage.blob import BlobClient
import requests
from bs4 import BeautifulSoup
import time

# Base URL for your Blob storage with the SAS token appended
base_blob_url = ""
sas_token = ""  # Paste your SAS token here

def fetch_cases(page_url):
    page = requests.get(page_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find all case links
    cases = []
    for result in soup.find_all('div', class_='result_title'):
        case_title = result.find('a').get_text().strip().replace('/', '')  # Replacing slashes with underscores for filenames
        case_link = "https://indiankanoon.org" + result.find('a')['href']
        cases.append((case_title, case_link))

    return cases

def fetch_judgment_and_metadata(case_url):
    case_page = requests.get(case_url)
    case_soup = BeautifulSoup(case_page.content, 'html.parser')

    # Extract judgment text
    judgment_text = ""
    for div in case_soup.find_all("div", class_="judgments"):
        judgment_text += div.get_text(separator='\n')

    # Extract metadata
    metadata_output = []
    tags_of_interest = ['h1', 'h2', 'h3', 'p', 'div', 'span']
    for tag in tags_of_interest:
        for element in case_soup.find_all(tag):
            text_content = element.get_text(strip=True)
            metadata_output.append({
                "tag": tag,
                "content": text_content
            })

    return judgment_text.strip(), metadata_output

def save_to_blob(case_title, judgment_text, metadata):
    # Create the full blob URL
    blob_url = f"{base_blob_url}/{case_title}.txt"
    
    # Create the BlobClient with the blob URL and SAS token as a credential
    blob_client = BlobClient.from_blob_url(blob_url, credential=sas_token)

    # Prepare the content for uploading
    content = f"Full Judgment:\n\n{judgment_text}\n\nMetadata:\n\n"
    for entry in metadata:
        content += f"Tag: {entry['tag']}, Content: {entry['content']}\n"

    # Upload to Blob Storage
    blob_client.upload_blob(content, overwrite=True)
    print(f"Judgment uploaded: {case_title}.txt")

def main(base_url):
    page_num = 1
    while True:
        cases = fetch_cases(base_url + f"&pagenum={page_num}")
        if not cases:
            break

        for case_title, case_link in cases:
            judgment_text, metadata = fetch_judgment_and_metadata(case_link)
            save_to_blob(case_title, judgment_text, metadata)

        page_num += 1
        time.sleep(2)

# Example usage
base_url = "https://indiankanoon.org/search/?formInput=doctypes:punjab%20fromdate:1-1-2023%20todate:%2031-12-2024"
main(base_url)