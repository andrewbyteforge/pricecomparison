from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from interface.forms import SearchForm
from .config import FILE_CONFIG
import threading
from loggingapp.custom_logging import Logger

from asda.asda import AsdaScraper
from tesco.tesco import TescoScraper
from sainsburys.sainsburys import SainsburysScraper
from morrisons.morrisons import MorrisonsScraper


class Scraper:
    def __init__(self, url_key: str, search_term: str):
        base_url = FILE_CONFIG.get(url_key)
        self.url = base_url.format(search_term)      
        self.log = Logger().logger
        self.log.info(f"Initialized URL for Morrisons scraper: {self.url}")
        self.log.info(f"Initialized URL for Asda scraper: {self.url}")
        self.log.info(f"Initialized URL for Tesco scraper: {self.url}")
        self.log.info(f"Initialized URL for Sainsburys scraper: {self.url}")


    def scrape(self):
        """
        This method is responsible for scraping the website and returning a list of products found on the page.
        
        Params:
        url_key:
        search_term:
        
        Exception:
        - If the URL is not valid or accessible it will raise an exception and log the error message to file
        
        Returns:
        None
       
        """
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
            self.log.error(f"An error occurred: {str(e)}")
            return None
        
    def run_asda_scraper(self, search_term:str):
        """
        Calls the asda scraper       
        
        Params:
        None
        
        Exception:
        If there are any issues with running the ASDA scraper it will raise an exception and log the error message to file
        
        Returns:
        None
        """       
        asda_scraper = AsdaScraper(search_term)
        asda_scraper.scrape()

    def run_tesco_scraper(self, search_term:str): 
        """
        Calls the tesco scraper       
        
        Params:
        None
        
        Exception:
        If there are any issues with running the ASDA scraper it will raise an exception and log the error message to file
        
        Returns:
        None
        """             
        tesco_scraper = TescoScraper(search_term)
        tesco_scraper.scrape()

    def run_sainsburys_scraper(self, search_term:str):    
        """
        Calls the sainsburys scraper       
        
        Params:
        None
        
        Exception:
        If there are any issues with running the ASDA scraper it will raise an exception and log the error message to file
        
        Returns:
        None
        """          
        sainsburys_scraper = SainsburysScraper(search_term)
        sainsburys_scraper.scrape()
        
    def run_morrisons_scraper(self, search_term:str):    
        """
        Calls the morrisons scraper       
        
        Params:
        None
        
        Exception:
        If there are any issues with running the ASDA scraper it will raise an exception and log the error message to file
        
        Returns:
        None
        """          
        morrisons_scraper = MorrisonsScraper(search_term)
        morrisons_scraper.scrape()
         
if __name__ == "__main__":    
    search_term = ""
    scraper = Scraper('some_url_key', search_term)
    
    # Create threads for each scraper method
    thread_asda = threading.Thread(target=scraper.run_asda_scraper, args=(search_term,))
    thread_tesco = threading.Thread(target=scraper.run_tesco_scraper, args=(search_term,))
    thread_sainsburys = threading.Thread(target=scraper.run_sainsburys_scraper, args=(search_term,))
    thread_morrisons = threading.Thread(target=scraper.run_morrisons_scraper, args=(search_term,))
    
    # Start all threads
    thread_asda.start()
    thread_tesco.start()
    thread_sainsburys.start()
    thread_morrisons.start()    


