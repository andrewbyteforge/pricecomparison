from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from .models import Product
from loggingapp.custom_logging import Logger
from django.shortcuts import render
from interface.forms import SearchForm




def display_database(request):
    products = Product.objects.all()
    form = SearchForm()
    return render(request, 'interface/products.html', {
        'products': products,
        'form': form,
        'search_query': None  
    })

# Delete all entries in the database.
def delete_all_entries(request):
    log = Logger().logger
    if request.method == 'POST':
        Product.objects.all().delete()
        log.info("All entries have been successfully deleted.")        
    return redirect(reverse('show_products'))


