from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Product
from django.shortcuts import render
from interface.forms import SearchForm
import logging
logger = logging.getLogger(__name__)


def display_database(request):
    products = Product.objects.all()
    form = SearchForm()
    return render(request, 'interface/products.html', {
        'products': products,
        'form': form,
        'search_query': None  
    })

def delete_all_entries(request):
    print("delete_all_entries view was called.")  # Add this line for debugging
    if request.method == 'POST':
        Product.objects.all().delete()
        logger.info("All entries have been successfully deleted.")
    return redirect('show_products')



