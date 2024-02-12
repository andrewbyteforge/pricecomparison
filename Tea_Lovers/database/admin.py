from django.contrib import admin
from .models import Product, BasketItem, Basket, Store

admin.site.register(Product)
admin.site.register(Basket)
admin.site.register(BasketItem)
admin.site.register(Store)
