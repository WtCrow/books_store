from django.urls import path, include
from .views import *


urlpatterns = [
    path('', index),

    # path('products/', products),
    # path('products/<str:product_type>/', products),
    # path('products/<str:product_type>/<str:category>/', products),
    # path('products/<str:product_type>/<str:category>/<int:product_id>', products),
    #
    # path('products/basket', products),
    #
    # path('products/auth', products),
    # path('products/profile', products),
    # path('logout/', logout),
]

handler404 = 'store.views.handler404'
