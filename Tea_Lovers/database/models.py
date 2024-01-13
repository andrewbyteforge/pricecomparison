from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    store = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)   
    
    class Meta:
        ordering = ['id']


    def __str__(self):
        return self.name

class Basket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='basket')

    def __str__(self):
        return f"Basket of {self.user.username}"

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in {self.basket}"
