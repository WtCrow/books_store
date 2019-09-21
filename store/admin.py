from django.contrib import admin
from .models import *


class SubcategoryAdmin(admin.ModelAdmin):
    search_fields = ('normalize_name', 'name')
    list_display = ('name', 'normalize_name')


class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name', )
    list_display = ('name', )


class BookAdmin(admin.ModelAdmin):
    search_fields = ('product', )
    list_display = ('product', )
    filter_horizontal = ('authors', )


class StationeryAdmin(admin.ModelAdmin):
    search_fields = ('product', )
    list_display = ('product', )


class CreationAdmin(admin.ModelAdmin):
    search_fields = ('product', )
    list_display = ('product', )


class ProductM2MInline(admin.TabularInline):
    model = ProductInOrder
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    search_fields = ('name', 'subcategory')
    list_filter = ('date_pub', )
    ordering = ('-date_pub', )
    list_display = ('name', 'subcategory', 'price',
                    'count_in_stock', 'picture_name', 'date_pub')


class OrderAdmin(admin.ModelAdmin):
    inlines = (ProductM2MInline, )
    search_fields = ('user', 'id')
    list_display = ('id', 'user')


class ProductInOrderAdmin(admin.ModelAdmin):
    search_fields = ('product', 'order', )
    list_display = ('product', 'order', 'count', 'price')


class BasketItemAdmin(admin.ModelAdmin):
    search_fields = ('user', 'product', )
    list_display = ('user', 'product', 'count')


admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Stationery, StationeryAdmin)
admin.site.register(Creation, CreationAdmin)
admin.site.register(BasketItem, BasketItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ProductInOrder, ProductInOrderAdmin)
