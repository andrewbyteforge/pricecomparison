from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('add_to_basket/', views.add_to_basket, name='add_to_basket'),
    path('remove_from_basket/', views.remove_from_basket, name='remove_from_basket'), 
]