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
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='product')
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='book')
    authors = models.ManyToManyField(Author)

    def get_absolute_url(self):
        url = reverse('book_page', kwargs={'pk': self.pk})
        return url

    def __str__(self):
        authors = ', '.join([str(author) for author in self.authors.all()])
        return f'{self.product}, {authors}'


class Creation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='creation')

    def get_absolute_url(self):
        url = reverse('creations_page', kwargs={'pk': self.pk})
        return url

    def __str__(self):
        return self.product


class Stationery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stationery')

    def get_absolute_url(self):
        url = reverse('stationery_page', kwargs={'pk': self.pk})
        return url

    def __str__(self):
        return self.product


class Order(models.Model):
    """Paid order"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order')
    products = models.ManyToManyField(Product, through='ProductInOrder')
    date_pub = models.DateTimeField(default=timezone.now)

    def __str__(self):
        orders = ', '.join([str(author) for author in self.products.all()])
        return f'user: {self.user} order_id: {self.pk} orders: {orders}'


class ProductInOrder(models.Model):
    """M2M class for Order and Product

    Use custom model for add count and price fields

    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_query_name='product_in_order')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_query_name='product_in_order')
    count = models.IntegerField()
    price = models.FloatField(validators=[MinValueValidator(0)], blank=False, default=0)

    def __str__(self):
        return f'Название: {self.product.name}; Количество: {self.count}; Цена за единицу: {self.price}'


class BasketItem(models.Model):
    """Current product some user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_query_name='basket_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_query_name='basket_items')
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
