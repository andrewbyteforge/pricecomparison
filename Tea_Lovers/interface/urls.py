from django.urls import path
from . import views


urlpatterns = [   
    path('', views.show_products, name='show_products'),  
    path('empty_basket/', views.empty_basket, name='empty_basket'),
    path('basket/', views.basket, name='basket'),
    path('pagination/', views.pagination, name='pagination'),        
    
]
