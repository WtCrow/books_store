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


admin.register(Product, ProductAdmin)
admin.register(Author, AuthorAdmin)
admin.register(Book, BookAdmin)
admin.register(Stationery, StationeryAdmin)
admin.register(Creation, CreationAdmin)
admin.register(BasketItem, BasketItemAdmin)
admin.register(Order, OrderAdmin)
