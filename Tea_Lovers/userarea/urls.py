from django.urls import path
from . import views


urlpatterns = [
    path('', views.register_user, name="register_user"),
    path('login_user/', views.login_user, name="login"),
    path('logout_user', views.logout_user, name="logout"),
    path('list_users/', views.list_users, name='list_users'),
]
