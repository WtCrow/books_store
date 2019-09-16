from django.db import models
from datetime import datetime
from django.conf import settings
from django.core.validators import MinValueValidator
from django.shortcuts import reverse


class Subcategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    normalize_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    description = models.TextField(blank=False)
    price = models.FloatField(validators=[MinValueValidator(0)])
    name = models.CharField(max_length=300, unique=True)
    count_in_stock = models.IntegerField(validators=[MinValueValidator(0)])
    picture_name = models.FileField(blank=True)
    date_pub = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Book(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    authors = models.ManyToManyField(Author)

    def get_absolute_url(self):
        url = reverse('book_page', kwargs={'pk': self.id})
        return url

    def __str__(self):
        authors_models = [str(author) for author in self.authors.all()]
        str_authors = ''.join(authors_models) if authors_models else ''
        return f'{self.product}, {str_authors}'


class Creation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def get_absolute_url(self):
        url = reverse('creations_page', kwargs={'pk': self.id})
        return url

    def __str__(self):
        return self.product


class Stationery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def get_absolute_url(self):
        url = reverse('stationery_page', kwargs={'pk': self.id})
        return url

    def __str__(self):
        return self.product


class Order(models.Model):
    # TODO если создали ордер, уменьшить количество продуктов
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product)
    count_product = models.IntegerField(validators=[MinValueValidator(0)], blank=False, default=0)
    result_price = models.FloatField(validators=[MinValueValidator(0)], blank=False, default=0)
    date_pub = models.DateTimeField(default=datetime.now())

    def __str__(self):
        return f'user: {self.user} product: {self.product} count: {self.count_product} price: {self.result_price}'


class BasketItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'user: {self.user} product: {self.product}'
