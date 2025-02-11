import requests
from bs4 import BeautifulSoup
import time
import json
from typing import Dict, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CourtScraper:
    def __init__(self):
        self.base_url = 'https://indiankanoon.org'
        self.browse_url = f'{self.base_url}/browse/'
        self.links: Dict[str, List[str]] = {}
        self.valid_court_names = ['Supreme Court of India']
        
    def get_soup(self, url: str) -> BeautifulSoup:
        try:
            page = requests.get(url)
            page.raise_for_status()
            return BeautifulSoup(page.content, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Error fetching URL {url}: {e}")
            return None

    def scrape_court_links(self):
        soup = self.get_soup(self.browse_url)
        if not soup:
            return

        results = soup.find_all(class_='browselist')
        if not results:
            logging.error("No courts found on the browse page")
            return

        for court in results[:1]:  # Limiting to first court as per original code
            link = court.find('a')
            if not link:
                continue
                
            court_name = link.text
            if court_name not in self.valid_court_names:
                continue
                
            court_url = f"{self.base_url}{link['href']}"
            self.links[court_name] = []
            self.scrape_years(court_name, court_url)

    def scrape_years(self, court_name: str, court_url: str):
        soup = self.get_soup(court_url)
        if not soup:
            return

        for year_link in soup.find_all(class_='browselist'):
            year_text = year_link.find('a').text
            try:
                year = int(year_text)
                if year < 1947 or year > 2020:
                    continue
                    
                logging.info(f"Processing year {year} for {court_name}")
                year_url = f"{self.base_url}{year_link.find('a')['href']}"
                self.scrape_months(court_name, year_url)
                logging.info(f"Completed year {year} for {court_name}")
                
            except ValueError:
                logging.warning(f"Invalid year format: {year_text}")
                continue

    def scrape_months(self, court_name: str, year_url: str):
        soup = self.get_soup(year_url)
        if not soup:
            return

        for month_link in soup.find_all(class_='browselist'):
            base_month_url = f"{self.base_url}{month_link.find('a')['href']}"
            self.scrape_pages(court_name, base_month_url)

    def scrape_pages(self, court_name: str, base_month_url: str):
        for page_num in range(100):  # Original range from code
            time.sleep(1)  # Rate limiting as per original code
            page_url = f"{base_month_url}&pagenum={page_num}"
            
            soup = self.get_soup(page_url)
            if not soup:
                continue

            result_urls = soup.find_all(class_='result_url')
            if not result_urls:
                break

            for result in result_urls:
                full_url = f"{self.base_url}{result['href']}"
                self.links[court_name].append(full_url)

    def save_links(self, filename: str):
        final_list = {name: self.links.get(name, []) for name in self.valid_court_names}
        
        try:
            with open(filename, "w") as outfile:
                json.dump(final_list, outfile, indent=4)
            logging.info(f"Successfully saved links to {filename}")
        except IOError as e:
            logging.error(f"Error saving links to file: {e}")

def main():
    scraper = CourtScraper()
    scraper.scrape_court_links()
    scraper.save_links("links_Supreme_Court.json")

if __name__ == "__main__":
    main()