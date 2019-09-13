from django.urls import path
from .views import *


urlpatterns = [
    path('', index),
    path('products/', products),
    path('product/', product),
    path('auth/', auth),
    path('profile/', profile),
    path('basket/', basket),
]
