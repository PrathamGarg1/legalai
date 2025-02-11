import os
import requests
from bs4 import BeautifulSoup
import time

# Function to fetch all cases from a single page
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

# Function to extract full judgment text from the case page along with metadata
def fetch_judgment_and_metadata(case_url):
    case_page = requests.get(case_url)
    case_soup = BeautifulSoup(case_page.content, 'html.parser')

    # Extracting the judgment text from the actual HTML tags
    judgment_text = ""
    for div in case_soup.find_all("div", class_="judgments"):  # Adjusted div class for judgment content
        judgment_text += div.get_text(separator='\n')

    # Extract metadata from the relevant tags (e.g., h1, h2, p, div, span)
    metadata_output = []
    tags_of_interest = ['h1', 'h2', 'h3', 'p', 'div', 'span']
    for tag in tags_of_interest:
        for element in case_soup.find_all(tag):
            text_content = element.get_text(strip=True)
            tag_name = element.name
            class_name = " ".join(element.get('class', []))
            element_id = element.get('id', '')
            metadata = {
                "tag": tag_name,
                "class": class_name,
                "id": element_id,
                "content": text_content
            }
            metadata_output.append(metadata)

    return judgment_text.strip(), metadata_output

# Function to save judgment and metadata to file
def save_to_file(case_title, judgment_text, metadata, output_folder):
    # Ensure the folder exists
    os.makedirs(output_folder, exist_ok=True)
    output_filename = os.path.join(output_folder, f"{case_title}.txt")

    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write("Full Judgment:\n\n")
        file.write(judgment_text + "\n\n")
        file.write("Metadata:\n\n")
        for entry in metadata:
            file.write(f"Tag: {entry['tag']}, Class: {entry['class']}, ID: {entry['id']}, Content: {entry['content']}\n")
    
    print(f"Judgment text and metadata saved to {output_filename}")

# Main function
def main(base_url, output_folder):
    page_num = 1
    while True:
        # Fetch cases from the current page
        cases = fetch_cases(base_url + f"&pagenum={page_num}")
        if not cases:
            break  # Exit when no more cases are found

        for case_title, case_link in cases:
            # Fetch the full judgment and metadata for each case
            judgment_text, metadata = fetch_judgment_and_metadata(case_link)
            
            # Save the judgment and metadata to a file
            save_to_file(case_title, judgment_text, metadata, output_folder)

        page_num += 1
        time.sleep(2)  # To avoid overloading the server

# Example usage
base_url = "https://indiankanoon.org/search/?formInput=doctypes:punjab%20fromdate:1-1-1948%20todate:%2031-12-2024"
output_folder = 'cases'
main(base_url, output_folder)
