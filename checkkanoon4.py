import requests
from bs4 import BeautifulSoup
import os


def get_page_metadata(url):
    """
    This function fetches the HTML of the page and extracts relevant metadata such as tags, classes, etc.
    """
    try:
        # Fetch the page content
        page = requests.get(url)
        page.raise_for_status()  # Check for request errors

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(page.content, 'html.parser')

        # Extract all text within relevant HTML tags and their metadata
        metadata_output = []
        
        # Define the tags to extract (you can add more tags as needed)
        tags_of_interest = ['h1', 'h2', 'h3', 'p', 'div', 'span']
        
        for tag in tags_of_interest:
            for element in soup.find_all(tag):
                # Extract text from the tag
                text_content = element.get_text(strip=True)

                # Extract tag-specific metadata like class, id, etc.
                tag_name = element.name
                class_name = " ".join(element.get('class', []))
                element_id = element.get('id', '')
                
                # Create metadata entry
                metadata = {
                    "tag": tag_name,
                    "class": class_name,
                    "id": element_id,
                    "content": text_content
                }
                metadata_output.append(metadata)

        return metadata_output
    
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []



def save_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)
    print(f"Judgment text saved to {filename}")

# Display the metadata
for entry in metadata:
    print(f"TAG: {entry['tag']}, CLASS: {entry['class']}, ID: {entry['id']}, CONTENT: {entry['content']}")

def main(url, output_folder):
    metadata = get_page_metadata(url)
    os.makedirs(output_folder, exist_ok=True)
    output_filename = os.path.join(output_folder, "judgment.txt")
    save_to_file(metadata, output_filename)

# Example usage
url = 'https://indiankanoon.org/doc/35844317/'  # Replace with the actual judgment URL
output_folder = 'withmetadata'  # Folder to store the text files
main(url, output_folder)