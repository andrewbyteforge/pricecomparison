from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC


import csv
from loggingapp.custom_logging import Logger
from database.models import Product
from interface.forms import SearchForm
from scraper.config import FILE_CONFIG
import decimal
import time



class MorrisonsScraper:
    def __init__(self, search_term):
        from scraper.scraper import Scraper
        self.scraper = Scraper('url_morrisons', search_term)
        self.log = Logger().logger

    def scrape(self):
            self.log.info('Starting Morrisons scraping process')
            driver = self.scraper.scrape()
            if driver:
                time.sleep(5)
                wait = WebDriverWait(driver, 10)
                try:
                    # Correct the selector to match the class names of the product items
                    products_container = driver.find_element(By.CSS_SELECTOR, '.fops.fops-regular.fops-shelf')
                    products = products_container.find_elements(By.CSS_SELECTOR, '.fops-item')
                    self.log.info(f"Number of products found: {len(products)}")

                    self.log.info(f"Number of products found: {len(products)}")
                    product_data_morrisons = []                    
                    for product in products:
                        try:
                            # Locate the name and price within the context of each product
                            name_elements = product.find_elements(By.CSS_SELECTOR, ".fop-title span")
                            price_elements = product.find_elements(By.CSS_SELECTOR, '.fop-price')
                            
                            name = name_elements[0].text if name_elements else "No Name"
                            price = price_elements[0].text if price_elements else "No Price"
                            
                            product_data_morrisons.append({'store': 'Morrisons', 'name': name, 'price': price})
                            self.log.info(f"Scraped product - Name: {name}, Price: {price}")
                            
                        except Exception as e:
                            self.log.error(f"Error occurred while processing a product: {e}")
                            continue  # ensures that one product error doesn't stop the loop
                except NoSuchElementException as e:
                    self.log.error(f"Error occurred while scraping Morrisons: {e}")
                finally:
                    # Save the data and close the driver outside of the try block
                    self.save_to_csv(product_data_morrisons, 'morrisons.csv')
                    self.save_to_database(product_data_morrisons)
                    self.log.info('Finished Morrisons scraping process')
                    driver.quit()

            if product_data_morrisons:
                self.save_to_csv(product_data_morrisons, 'Morrisons.csv')
                self.save_to_database(product_data_morrisons)
                self.log.info('Finished Morrisons scraping process')
            
            
            
    def clean_price(self, price_str: str):
        try:
            self.log.debug(f"Raw price string: {price_str}")  # Log the raw price string
            # Remove the currency symbol and any other non-numeric characters, except for the decimal point
            cleaned_price = ''.join(filter(lambda x: x.isdigit() or x == '.', price_str))
            # Convert the cleaned string to a decimal
            return decimal.Decimal(cleaned_price)
        except Exception as e:
            self.log.warning(f"Could not clean price string: {e}")
            # Return a default value in case of error, which is a valid decimal
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

            
    def save_to_database(self, product_data_morrisons):                
        for item in product_data_morrisons:
            if item['name'] == "No Name" or item['price'] == "No Price":
                self.log.warning("Skipping database update due to missing product data")
                continue
            try:
                # Clean the price and convert to decimal
                cleaned_price = self.clean_price(item['price'])
                # Save the product with the cleaned price
                product, created = Product.objects.get_or_create(
                    store='Morrisons',
                    name=item['name'],
                    defaults={'price': cleaned_price}  # Ensure cleaned_price is a Decimal
                )
                if created:
                    self.log.info(f"Created new product: {product.name}")
                else:
                    self.log.info(f"Updated existing product: {product.name}")
            except Exception as e:
                self.log.error(f"Database Error: {e}")
