from django.urls import path
from .views import *


handler404 = 'store.views.custom_handler404'

urlpatterns = [
    path('', index, name='index'),

    path('products/search/', FindBook.as_view(), name='root_search'),
    path('products/search/books', FindBook.as_view(), name='root_search'),
    path('products/search/stationery', FindStationery.as_view(), name='root_search'),
    path('products/search/creations', FindCreation.as_view(), name='root_search'),
    path('products/search/<str:category>', custom_handler404, name='root_search'),

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

]
