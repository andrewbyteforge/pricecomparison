import threading
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import SearchForm
from database.models import Product
from asda.asda import AsdaScraper
from tesco.tesco import TescoScraper
from sainsburys.sainsburys import SainsburysScraper
from loggingapp.custom_logging import Logger
from django.http import HttpRequest
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .forms import SearchForm
from database.models import Product, BasketItem
import threading
from django.core.paginator import Paginator

# Logger instance
logger = logging.getLogger(__name__)


# Creates an instance of the scraper calling the main class


def run_asda_scraper(search_query: str, max_retries=3):
    """
    This function is used to start a new thread for running the ASDA Scraper and returns the results in JSON format. 

    Params:
    search_query is the inputted data
    max_retries is the amount of times the function will try again.   

    Exception:
    If there are any errors in running the scrape it will retry for a maximum of 3 attempts before stopping.

    Returns:
    A list containing all products found from the search query.
    """
    retries = 0
    while retries < max_retries:
        try:
            asda_scraper = AsdaScraper(search_query)
            asda_scraper.scrape()
            break  # If scrape is successful, exit the loop
        except ConnectionError as e:
            retries += 1
            Logger().logger.error(
                f"Retry {retries}/{max_retries} for Asda scraper failed: {e}")
            time.sleep(5)
            if retries >= max_retries:
                Logger().logger.error("Max retries reached for Asda scraper")

# Creates an instance of the scraper calling the main class


def run_tesco_scraper(search_query: str, max_retries=3):
    """
    This function is used to start a new thread for running the ASDA Scraper and returns the results in JSON format. 

    Params:
    search_query is the inputted data
    max_retries is the amount of times the function will try again.   

    Exception:
    If there are any errors in running the scrape it will retry for a maximum of 3 attempts before stopping.

    Returns:
    A list containing all the products found by the scraping process.
    """
    retries = 0
    while retries < max_retries:
        try:
            tesco_scraper = TescoScraper(search_query)
            tesco_scraper.scrape()
            break  # If scrape is successful, exit the loop
        except ConnectionError as e:
            retries += 1
            Logger().logger.error(
                f"Retry {retries}/{max_retries} for Tesco scraper failed: {e}")
            time.sleep(5)
            if retries >= max_retries:
                Logger().logger.error("Max retries reached for Tesco scraper")

# Creates an instance of the scraper calling the main class


def run_sainsburys_scraper(search_query: str, max_retries=3):
    """
    This function is used to start a new thread for running the ASDA Scraper and returns the results in JSON format. 

    Params:
    search_query is the inputted data
    max_retries is the amount of times the function will try again.   

    Exception:
    If there are any errors in running the scrape it will retry for a maximum of 3 attempts before stopping.

    Returns:
    A list containing all the products found by the scraping process.
    """
    retries = 0
    while retries < max_retries:
        try:
            sainsburys_scraper = SainsburysScraper(search_query)
            sainsburys_scraper.scrape()
            break  # If scrape is successful, exit the loop
        except ConnectionError as e:
            retries += 1
            Logger().logger.error(
                f"Retry {retries}/{max_retries} for Sainsburys scraper failed: {e}")
            time.sleep(5)
            if retries >= max_retries:
                Logger().logger.error("Max retries reached for Sainsburys scraper")


@login_required
def show_products(request):
    form = SearchForm(request.POST or None)
    search_query = request.GET.get('query', '')
    context = {'form': form, 'search_query': search_query}
    user_basket_items = []

    try:
        if request.method == "POST" and form.is_valid():
            search_query = form.cleaned_data['search_query']
            if not search_query:
                return redirect('show_products')

            search_terms = [term.strip() for term in search_query.split(',')]           
            threads = []
            for term in search_terms:
                threads.append(threading.Thread(target=run_asda_scraper, args=(term,)))
                threads.append(threading.Thread(target=run_tesco_scraper, args=(term,)))
                threads.append(threading.Thread(target=run_sainsburys_scraper, args=(term,)))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            return redirect(f'/products/?query={search_query}')
        
               # Calculate the total prices for each store
        tesco_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Tesco')
        asda_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Asda')
        sainsburys_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Sainsburys')   

        tesco_products = Product.objects.filter(store='Tesco', name__icontains=search_query).order_by('id')
        asda_products = Product.objects.filter(store='Asda', name__icontains=search_query).order_by('id')
        sainsburys_products = Product.objects.filter(store='Sainsburys', name__icontains=search_query).order_by('id')

        items_per_page = 15  # 5 items from each store
        paginator = Paginator(tesco_products.union(asda_products, sainsburys_products, all=True), items_per_page)
        current_page = request.GET.get('page', 1)
        page_items = paginator.get_page(current_page)

        start_index = (page_items.number - 1) * 5
        end_index = start_index + 5
        tesco_page_items = tesco_products[start_index:end_index]
        asda_page_items = asda_products[start_index:end_index]
        sainsburys_page_items = sainsburys_products[start_index:end_index]

        if request.user.is_authenticated:
            user_basket_items = BasketItem.objects.filter(basket__user=request.user)
            
            
            # Calculate the total prices for each store
            tesco_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Tesco')
            asda_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Asda')
            sainsburys_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Sainsburys')
        else:
            user_basket_items = []
            tesco_total = asda_total = sainsburys_total = 0
            

        context.update({
            'sainsburys_total': sainsburys_total,
            'asda_total': asda_total,
            'tesco_total': tesco_total,
            'tesco_products': tesco_page_items,
            'asda_products': asda_page_items,
            'sainsburys_products': sainsburys_page_items,
            'list_per_page': page_items,
            'user_basket_items': user_basket_items,
            
        })
    except Exception as e:
        logger.error(f"Error in show_products view: {e}", exc_info=True)

    return render(request, 'interface/products.html', context)




@login_required
def empty_basket(request):
    if request.method == "POST":
        BasketItem.objects.filter(basket__user=request.user).delete()        
        return redirect('/products/')    
    return redirect('home')








