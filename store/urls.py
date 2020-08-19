from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *


router = DefaultRouter()
router.register(r'test', Basket)
router.register(r'test/<int:pk>/', Basket)

urlpatterns = [
    path('store/api/v1/', include(router.urls)),

    path('', index, name='index'),

    path('products/search/', Find.as_view(), name='search'),

    path('products/books/<str:subcategory>/', BookCategory.as_view(), name='root_books'),
    path('products/books/', BookCategory.as_view(), name='root_books'),

    path('products/stationery/<str:subcategory>/', StationeryCategory.as_view(), name='root_stationery'),
    path('products/stationery/', StationeryCategory.as_view(), name='root_stationery'),

    path('products/creations/<str:subcategory>/', CreationCategory.as_view(), name='root_creations'),
    path('products/creations/', CreationCategory.as_view(), name='root_creations'),

    path('products/books/product/<int:pk>', BookPage.as_view(), name='book_page'),
    path('products/stationery/product/<int:pk>', StationeryPage.as_view(), name='stationery_page'),
    path('products/creations/product/<int:pk>', CreationPage.as_view(), name='creations_page'),

    path('products/<str:category>/<str:subcategory>/', custom_handler404, name='root_category'),
    path('products/<str:category>/', custom_handler404, name='root_category'),

    path('basket/', GetBasketPage.as_view(), name='basket'),
    path('basket/buy/', buy_product, name='buy_products'),

    path('purchase_story/', StoryPurchase.as_view(), name='story'),
]
