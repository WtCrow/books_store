from django.db import models
from datetime import datetime
from django.conf import settings


class Product(models.Model):
    description = models.TextField(blank=False)
    price = models.DecimalField()
    name = models.CharField(max_length=100)
    count_in_stock = models.IntegerField()
    picture_name = models.FileField()
    date_pub = models.DateTimeField(default=datetime.now())


class Book(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.CharField(max_length=25)


class Creation(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)


class Stationery(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)


class Order(models.Model):
    models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    models.ManyToManyField(Product, on_delete=models.CASCADE)
    date_pub = models.DateTimeField(default=datetime.now())


class BasketItem(models.Model):
    models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    models.ForeignKey(Product, on_delete=models.CASCADE)
