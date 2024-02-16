from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import csv
from database.models import Product
from interface.forms import SearchForm
from scraper.config import FILE_CONFIG
import decimal

class TescoScraper:
    """
    This class is responsible for scraping the data from tesco website and storing it in a CSV file.
    """
    def __init__(self, search_term:str):
        """
        Initializes the object with the given search term.
        """
        from scraper.scraper import Scraper
        self.scraper = Scraper('url_tesco', search_term)
        # Initialize logger
        


    def scrape(self):
        """
        This method is responsible for scraping data from the Tesco website and storing it in a CSV file.

        It extracts product details like name and price, saves them to a CSV file, and updates the database.

        Params: 
        self (TescoScraper): The instance of TescoScraper on which this method is called.

        Raises: 
        NoSuchElementException: If an expected HTML element is not found during scraping.
        Exception: For general exceptions, particularly when saving data to the database.

        Returns:
        None: This method does not return anything.
        """   
        self.log.info('Starting Tesco scraping process')
        driver = self.scraper.scrape()
        if driver:
            try:
                products = driver.find_elements(By.TAG_NAME, 'li')
                product_data_tesco = []
                for product in products:
                    name_elements = product.find_elements(
                        By.CSS_SELECTOR,
                        'a span.styled__Text-sc-1i711qa-1')
                    price_elements = product.find_elements(
                        By.CSS_SELECTOR,
                        'p.styled__StyledHeading-sc-119w3hf-2')
                    if name_elements and price_elements:
                        name = name_elements[0].text
                        price = price_elements[0].text
                        # Add store name to each product entry
                        product_data_tesco.append({'store': 'Tesco', 'name': name,
                                             'price': price})
                self.save_to_csv(product_data_tesco, 'tesco.csv')
            except NoSuchElementException as e:
                self.log.error(f"Error occurred while scraping Tesco: {e}")
            finally:
                driver.quit()

            if product_data_tesco:
                try:
                    self.save_to_database(product_data_tesco)                
                    self.log.info('Finished Tesco scraping process')
                except Exception as e:                    
                    self.log.error(f"Data not saved to database ERROR! {e}")
                    
    def clean_price(self, price_str: str):
        try:
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

            
    def save_to_database(self, product_data_tesco):
        for item in product_data_tesco:
            try:
                # Clean the price and convert to decimal
                cleaned_price = self.clean_price(item['price'])
                # Save the product with the cleaned price
                product, created = Product.objects.get_or_create(
                    store='Tesco',
                    name=item['name'],
                    defaults={'price': cleaned_price}  # Ensure cleaned_price is a Decimal
                )
                if created:
                    self.log.info(f"Created new product: {product.name}")
                else:
                    self.log.info(f"Updated existing product: {product.name}")
            except Exception as e:
                self.log.error(f"Database Error: {e}")