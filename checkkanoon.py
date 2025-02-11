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
        case_title = result.find('a').get_text()
        case_link = "https://indiankanoon.org" + result.find('a')['href']
        cases.append((case_title, case_link))
    
    return cases

# Function to extract full judgment text from the case page
def fetch_judgment(case_url):
    case_page = requests.get(case_url)
    case_soup = BeautifulSoup(case_page.content, 'html.parser')
    
    # Assuming full judgment is in a div with id "content"
    judgment_div = case_soup.find('div', id='content')
    if judgment_div:
        return judgment_div.get_text()
    else:
        return "Content not found"

# Initial page URL
base_url = "https://indiankanoon.org/search/?formInput=doctypes%3A%20punjab%20fromdate%3A%201-9-2022%20todate%3A%2030-9-2022"

# Pagination loop
page_num = 1
while True:
    # Fetch cases from the current page
    cases = fetch_cases(base_url + f"&pagenum={page_num}")
    if not cases:
        break  # Exit when no more cases are found
    
    for case_title, case_link in cases:
        # Fetch the full judgment for each case
        judgment_text = fetch_judgment(case_link)
        # Save the case title and judgment text
        with open(f"cases/{case_title}.txt", 'w', encoding='utf-8') as f:
            f.write(judgment_text)
    
    page_num += 1
    time.sleep(2)  # To avoid overloading the server
