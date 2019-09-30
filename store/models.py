from django.core.validators import MinValueValidator
from django.db.models import signals, Q
from django.shortcuts import reverse
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django.db import models


class Subcategory(models.Model):
    """Subcategory product (book->programming)"""
    name = models.CharField(max_length=50, unique=True, db_index=True)
    normalize_name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.normalize_name


class Product(models.Model):
    """Base class for products"""
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    description = models.TextField(blank=False)
    price = models.FloatField(validators=[MinValueValidator(0)])
    name = models.CharField(max_length=300, unique=True, db_index=True)
    count_in_stock = models.IntegerField(validators=[MinValueValidator(0)])
    picture_name = models.FileField(blank=True)
    date_pub = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=50, db_index=True)

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='ProductInOrder')
    date_pub = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'user: {self.user} order_id: {self.id}'


class ProductInOrder(models.Model):
    """M2M class for Order and Product"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    count = models.IntegerField()
    price = models.FloatField(validators=[MinValueValidator(0)], blank=False, default=0)

    def __str__(self):
        return f'Название: {self.product.name}; Количество: {self.count}; Цена за единицу: {self.price}'


class BasketItem(models.Model):
    """Current products some user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count = models.IntegerField()

    def __str__(self):
        return f'user: {self.user} product: {self.product}'


@receiver(signals.pre_save, sender=ProductInOrder)
def change_count_in_stock(sender, instance, **kwargs):
    """Change count products before add new ProductInOrder

    Edit access count products in stock
    and change count products in basket other users.

    """
    instance.product.count_in_stock = instance.product.count_in_stock - instance.count
    instance.product.save()

    count_in_stock = instance.product.count_in_stock
    # delete from basket or reduce count
    if count_in_stock == 0:
        BasketItem.objects.filter(product=instance.product).exclude(user=instance.order.user).delete()
    else:
        BasketItem.objects.filter(Q(product=instance.product) & Q(count__gt=count_in_stock))\
            .exclude(user=instance.order.user).update(count=count_in_stock)


classes_product_models = [Book, Stationery, Creation]
