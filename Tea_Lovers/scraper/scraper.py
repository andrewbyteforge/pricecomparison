from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import threading
from loggingapp.custom_logging import Logger
from .config import FILE_CONFIG
from asda.asda import AsdaScraper
from tesco.tesco import TescoScraper
from sainsburys.sainsburys import SainsburysScraper
from morrisons.morrisons import MorrisonsScraper  

class Scraper:
    def __init__(self, store: str, search_term: str):
        self.store = store.capitalize()  # Capitalize store name for consistency
        base_url = FILE_CONFIG.get(self.store.lower())
        self.url = base_url.format(search_term)
        self.log = Logger().logger
        self.log.info(f"Initialized URL for {self.store} scraper: {self.url}")
        self.search_term = search_term

    def scrape(self):
        try:
            options = Options()
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
            options.add_argument(f'user-agent={user_agent}')
            driver = webdriver.Chrome(options=options)
            driver.get(self.url)
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(10)
            return driver
        except Exception as e:
            self.log.error(f"An error occurred while scraping {self.store}: {str(e)}")
            return None

    def run_scraper(self):
        self.log.info(f"Running scraper for {self.store}")
        scraper_class = {
            'Asda': AsdaScraper,
            'Tesco': TescoScraper,
            'Sainsburys': SainsburysScraper,
            'Morrisons': MorrisonsScraper
        }.get(self.store)

        if scraper_class:
            scraper = scraper_class(self.search_term)
            scraper.scrape()
        else:
            self.log.error(f"No scraper found for {self.store}")


if __name__ == "__main__":    
    search_term = "your_search_term"
    stores = ['Asda', 'Tesco', 'Sainsburys', 'Morrisons']
    
    for store in stores:
        scraper = Scraper(store, search_term)
        thread = threading.Thread(target=scraper.run_scraper)
        thread.start()
