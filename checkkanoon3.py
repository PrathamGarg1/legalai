import requests
from bs4 import BeautifulSoup
import os

def download_judgment_page(url):
    # Download the webpage content
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def extract_text(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the main content within <div> and <p> tags
    judgment_text = ""
    
    # Extracting the text from <div class="judgments"> as it's the main content
    for div in soup.find_all("div", class_="judgments"):
        judgment_text += div.get_text(separator='\n')

    return judgment_text.strip()

def save_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Judgment text saved to {filename}")

def main(url, output_folder):
    # Step 1: Download the webpage
    html_content = download_judgment_page(url)

    if html_content:
        # Step 2: Extract the relevant text
        judgment_text = extract_text(html_content)

        # Step 3: Save the text into a file
        os.makedirs(output_folder, exist_ok=True)
        output_filename = os.path.join(output_folder, "judgment.txt")
        save_to_file(judgment_text, output_filename)

# Example usage
url = 'https://indiankanoon.org/doc/35844317/'  # Replace with the actual judgment URL
output_folder = 'judgment_files'  # Folder to store the text files
main(url, output_folder)
