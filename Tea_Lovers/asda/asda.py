from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv
from database.models import Product
from interface.forms import SearchForm
from scraper.config import FILE_CONFIG
from decimal import Decimal, InvalidOperation
import decimal 
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AsdaScraper:
    def __init__(self, search_term: str):
        """
        Initializes the class with a given search term and sets up the driver for Selenium WebDriver. Initialises the logger
        """
        from scraper.scraper import Scraper
        self.scraper = Scraper('url_asda', search_term)       
        self.log = Logger().logger

    def scrape(self):
        self.log.info('Starting Asda scraping process')
        driver = self.scraper.scrape()
        if driver:
            try:
                # Use WebDriverWait to wait for the product elements to be present
                wait = WebDriverWait(driver, 10)
                products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.co-item--rest-in-shelf')))
                
                product_data_asda = []
                for product in products:
                    # Extract product name and price
                    name_elements = product.find_elements(By.CSS_SELECTOR, 'div > div > div > div > h3 > a')
                    price_elements = product.find_elements(By.CSS_SELECTOR, 'div > div > div > div > span > strong')
                    
                    if name_elements and price_elements:
                        name = name_elements[0].text if name_elements else "No Name"
                        price = self.clean_price(price_elements[0].text)  # Call clean_price method
                        product_data_asda.append({'store': 'Asda', 'name': name, 'price': price})
                
                # Save data to CSV and database
                self.save_to_csv(product_data_asda, 'asda.csv')
            except (NoSuchElementException, TimeoutException) as e:
                self.log.error(f"Error occurred while scraping Asda: {e}")
            finally:
                driver.quit()
            
            if product_data_asda:
                try:
                    self.save_to_database(product_data_asda)
                    self.log.info('Finished Asda scraping process')
                except Exception as e:
                    self.log.error(f"Data not saved to database ERROR! {e}")



    def clean_price(self, price_str):
        try:
            # Check if price_str is already a Decimal
            if isinstance(price_str, decimal.Decimal):
                return price_str

            # Otherwise, clean and convert the string to Decimal
            cleaned_price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str))
            return Decimal(cleaned_price)
        except Exception as e:
            self.log.warning(f"Could not clean price string: {e}")
            return decimal.Decimal('0.00')



    def save_to_csv(self, data, filename):
        """
        Save the collected data into CSV file
        
        Params:
        data (list of dictionaries): List containing dictionaries with keys ['store','name','price']
        filename (string): File path where to store the csv file
        
        Exception:
        IOError: If there is an error opening/writing to the specified file.
        
        Returns:
        None
        """
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['store', 'name', 'price'])
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
        except FileNotFoundError:
            self.log.error(f"File not found: {filename}")
        except PermissionError:
            self.log.error(f"Permission denied: Unable to write to {filename}")
        except IOError as e:
            self.log.error(f"I/O error: {e}")
        except csv.Error as e:
            self.log.error(f"CSV writing error: {e}")

            
    def save_to_database(self, product_data_asda):
        for item in product_data_asda:
            try:
                # Clean the price and convert to decimal
                cleaned_price = self.clean_price(item['price'])
                # Save the product with the cleaned price
                product, created = Product.objects.get_or_create(
                    store='Asda',
                    name=item['name'],
                    defaults={'price': cleaned_price}  # Ensure cleaned_price is a Decimal
                )
                if created:
                    self.log.info(f"Created new product: {product.name}")
                else:
                    self.log.info(f"Updated existing product: {product.name}")
            except Exception as e:
                self.log.error(f"Database Error: {e}")



