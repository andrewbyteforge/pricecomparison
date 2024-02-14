from django.urls import path
from . import views 


urlpatterns = [
    path('', views.ProductView.show_products, name='show_products'),
    path('empty_basket/', views.BasketView.empty_basket, name='empty_basket'),
    path('basket/', views.BasketView.basket, name='basket'),
    path('get_paginated_products_for_store/', views.ProductPagination, name='get_paginated_products_for_store'), 
    path('calculate_asda_total/', views.calculate_asda_total, name='calculate_asda_total'),
    path('api/get_basket_contents/', views.get_basket_contents, name='get_basket_contents'),
]

      
    

