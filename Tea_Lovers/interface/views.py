from .forms import SearchForm
from database.models import Product, BasketItem
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse



import logging

# Logger instance
logger = logging.getLogger(__name__)


class ProductPagination:
    """
    A utility class for paginating a queryset of products.

    This class provides a static method to paginate a list of products based on the specified number
    of items per page and the current page number obtained from the request's GET parameters.

    Parameters:
        products (QuerySet): The queryset of products to paginate.
        items_per_page (int): The number of products to display per page.
        request (HttpRequest): The HTTP request object containing the page number in its GET parameters.

    Returns:
        Page: A Page object containing the products for the requested page.

    Usage:
        paginator = ProductPagination()
        page_number = request.GET.get('page', 1)
        products = Product.objects.all()  # Query your products here
        paginated_page = paginator.paginate_products(products, items_per_page, request)
    """  
    @staticmethod
    def paginate_products(products, items_per_page, request):
        # Log the start of pagination process
        logger.info("Starting pagination of products.")

        # Create a paginator instance
        paginator = Paginator(products, items_per_page)

        # Get the current page number from the request's GET parameters, default to 1
        page_number = request.GET.get('page', 1)
        logger.debug(f"Fetching page {page_number}.")

        # Attempt to return the Page object for the requested page
        try:
            page = paginator.get_page(page_number)
            return page
        except Exception as e:
            # Log any errors that occur during pagination
            logger.error(f"Error during pagination: {e}", exc_info=True)
            return None

class ProductView:   
    @staticmethod
    def get_paginated_products_for_store(store_name, search_query, page_number, items_per_page=5):
        
        # Log the start of the product retrieval and pagination process
        logger.info(f"Fetching paginated products for store: {store_name} with search query: '{search_query}'")
        
        # name__icontains=search_query case sensitive partial matches
        products = Product.objects.filter(store=store_name, name__icontains=search_query).order_by('id')
        
        # Log the number of products found before pagination
        logger.debug(f"Found {products.count()} products matching criteria.")

        paginator = Paginator(products, items_per_page)
        
        # Attempt to paginate and catch any potential errors
        try:
            paginated_page = paginator.get_page(page_number)
            logger.info(f"Returning page {page_number} of paginated products.")
            return paginated_page
        except Exception as e:
            logger.error(f"Error during pagination: {e}", exc_info=True)
            # Depending on your error handling strategy, you might return an empty page, raise the exception, etc.
            return None
            
    @staticmethod
    def show_products(request):
        logger.info("Showing products with potential search query.")
        form = SearchForm(request.GET or None)
        page_number = request.GET.get('page', 1)  
        
        # search query by user and checkbox store        
        search_query = request.GET.get('search_query', '')
        selected_stores = request.GET.getlist('store')      
        # Define items_per_page
        items_per_page = 5 
        
        # Initialize a dictionary to hold paginated products from each store
        paginated_products = {}
        
        # start with an empty query
        products = Product.objects.none()  
         # Fetch products for all selected stores
        if 'Tesco' in selected_stores:
             products |= Product.objects.filter(store='Tesco', name__icontains=search_query)
        if 'Asda' in selected_stores:
             products |= Product.objects.filter(store='Asda', name__icontains=search_query)
        if 'Morrisons' in selected_stores:
             products |= Product.objects.filter(store='Morrisons', name__icontains=search_query)
        if 'Sainsburys' in selected_stores:
             products |= Product.objects.filter(store='Sainsburys', name__icontains=search_query)

        # # Fetch and paginate products for each store
        tesco_products = ProductView.get_paginated_products_for_store('Tesco', search_query, page_number, items_per_page)
        asda_products = ProductView.get_paginated_products_for_store('Asda', search_query, page_number, items_per_page)
        sainsburys_products = ProductView.get_paginated_products_for_store('Sainsburys', search_query, page_number, items_per_page)
        morrisons_products = ProductView.get_paginated_products_for_store('Morrisons', search_query, page_number, items_per_page)

        # # Combine all products
        # all_products = tesco_products, asda_products, sainsburys_products, morrisons_products
        
        # Pass Paginator object to template context
        # Now paginate this combined queryset
        paginator = Paginator(products.order_by('id'), items_per_page)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
            
        
        
        selected_stores = request.GET.getlist('store')    
        
        context = {
            'form': form,            
            'search_query': search_query,
            'selected_stores': selected_stores,        
        
            'tesco_products': tesco_products,
            'asda_products': asda_products,
            'sainsburys_products': sainsburys_products,
            'morrisons_products': morrisons_products,    
                                   
            'page_obj': page_obj,  
        }

        return render(request, 'interface/products.html', context)


class BasketView:
    @staticmethod
    @login_required
    def empty_basket(request):
        if request.method == "POST":
            items_deleted = BasketItem.objects.filter(basket__user=request.user).delete()
            logger.info(f"User {request.user.username} emptied their basket, {items_deleted[0]} items deleted.")
            return redirect('/products/')
        logger.warning(f"User {request.user.username} attempted to empty basket via a non-POST request.")
        return redirect('home')

    @staticmethod
    def basket(request):
        logger.info(f"User {request.user.username if request.user.is_authenticated else 'Anonymous'} accessed the basket page.")
        return render(request, 'basket.html')



@login_required
def calculate_asda_total(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            user_basket_items = BasketItem.objects.filter(basket__user=request.user, product__store='Asda')
            if not user_basket_items.exists():
                return JsonResponse({'total_price': 0.0})  # Explicitly return £0.00 if the basket is empty
            total_price = sum(item.product.price * item.quantity for item in user_basket_items)
            return JsonResponse({'total_price': float(total_price)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'This endpoint requires an AJAX request.'}, status=400)


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def get_basket_contents(request):
    try:
        basket_items = BasketItem.objects.filter(basket__user=request.user).select_related('product')
        items_data = [{
            'id': item.id,
            'name': item.product.name,
            'price': item.product.price,
            'quantity': item.quantity,
            'store': item.product.store,
        } for item in basket_items]
        return JsonResponse({'items': items_data, 'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


