from django.contrib import admin
from .models import *


class ProductAdmin(admin.ModelAdmin):
    pass


class AuthorAdmin(admin.ModelAdmin):
    pass


class BookAdmin(admin.ModelAdmin):
    pass


class StationeryAdmin(admin.ModelAdmin):
    pass


class CreationAdmin(admin.ModelAdmin):
    pass


class BasketItemAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):
    pass


class CountProductInOrderAdmin(admin.ModelAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Stationery, StationeryAdmin)
admin.site.register(Creation, CreationAdmin)
admin.site.register(BasketItem, BasketItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductInOrder, CountProductInOrderAdmin)
