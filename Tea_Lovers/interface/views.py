from .forms import SearchForm
from database.models import Product, BasketItem

from asda.asda import AsdaScraper
from tesco.tesco import TescoScraper
from sainsburys.sainsburys import SainsburysScraper
from morrisons.morrisons import MorrisonsScraper

from loggingapp.custom_logging import Logger
import logging

import threading
import time
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect

# Logger instance
logger = logging.getLogger(__name__)

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
                
def run_morrisons_scraper(search_query: str, max_retries=3):
    """
    This function is used to start a new thread for running the Morrisons Scraper and returns the results in JSON format. 

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
            morrisons_scraper = MorrisonsScraper(search_query)
            morrisons_scraper.scrape()
            break  # If scrape is successful, exit the loop
        except ConnectionError as e:
            retries += 1
            Logger().logger.error(
                f"Retry {retries}/{max_retries} for Morrisons scraper failed: {e}")
            time.sleep(5)
            if retries >= max_retries:
                Logger().logger.error("Max retries reached for Morrisons scraper")

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
                threads.append(threading.Thread(target=run_morrisons_scraper, args=(term,)))
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()
            return redirect(f'/products/?query={search_query}')        

        tesco_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Tesco')
        asda_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Asda')
        sainsburys_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Sainsburys')   
        morrisons_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Morrisons')  
        
        tesco_products = Product.objects.filter(store='Tesco', name__icontains=search_query).order_by('id')
        asda_products = Product.objects.filter(store='Asda', name__icontains=search_query).order_by('id')
        sainsburys_products = Product.objects.filter(store='Sainsburys', name__icontains=search_query).order_by('id')
        morrisons_products = Product.objects.filter(store='Sainsburys', name__icontains=search_query).order_by('id')

        items_per_page = 20  # 5 items from each store
        ordered_queryset = tesco_products.union(asda_products, sainsburys_products, morrisons_products, all=True).order_by('id')
        paginator = Paginator(ordered_queryset, items_per_page)
        current_page = request.GET.get('page', 1)
        page_items = paginator.get_page(current_page)

        start_index = (page_items.number - 1) * 5
        end_index = start_index + 5
        tesco_page_items = tesco_products[start_index:end_index]
        asda_page_items = asda_products[start_index:end_index]
        sainsburys_page_items = sainsburys_products[start_index:end_index]
        morrisons_page_items = morrisons_products[start_index:end_index]

        if request.user.is_authenticated:
            user_basket_items = BasketItem.objects.filter(basket__user=request.user)            
            # Calculate the total prices for each store
            tesco_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Tesco')
            asda_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Asda')
            sainsburys_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Sainsburys')
            morrisons_total = sum(item.product.price for item in user_basket_items if item.product.store == 'Morrisons')
        else:
            user_basket_items = []
            tesco_total = asda_total = sainsburys_total = 0            

        context.update({
            'morrisons_total': morrisons_total,
            'sainsburys_total': sainsburys_total,
            'asda_total': asda_total,
            'tesco_total': tesco_total,
            
            'tesco_products': tesco_page_items,
            'asda_products': asda_page_items,
            'sainsburys_products': sainsburys_page_items,
            'morrisons_products': morrisons_page_items,
            
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


def basket(request):      
    return render(request, 'basket.html')

def pagination(request):      
    return render(request, 'pagination.html')






