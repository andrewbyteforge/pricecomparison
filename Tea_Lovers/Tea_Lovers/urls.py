"""
URL configuration for Tea_Lovers project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from userarea import views as userarea_views

urlpatterns = [ 
    # Admin urls
    path('admin/', admin.site.urls),    
    
    # Set the root URL to the login view
    path('', userarea_views.login_user, name='login'),     
    # user area urls (excluding the login view if it's now the root)
    path('userarea/', include('userarea.urls')), 
    
    path('', include('loggingapp.urls')),               
    
    # Asda urls
    path('asda/', include('asda.urls')),     
      
    # Tesco urls
    path('', include('tesco.urls')), 
      
    # Sainsburys urls
    path('', include('sainsburys.urls')), 
    
    # Morrisons urls
    path('', include('morrisons.urls')),     
    
    
    # Interface urls
    path('interface/', include('interface.urls')),
    path('products/', include('interface.urls')),
    
    
    # database urls 
    path('database/', include('database.urls')), 
]
