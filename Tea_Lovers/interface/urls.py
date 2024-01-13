from django.urls import path
from .views import empty_basket, show_products


urlpatterns = [   
    path('', show_products, name='show_products'),  
    path('empty_basket/', empty_basket, name='empty_basket'),   
    
]
