from django.urls import path
from . import views

urlpatterns = [    
    path('delete-all/', views.delete_all_entries, name='delete_all_entries'),
    path('display-database/', views.display_database, name='display_database')
]