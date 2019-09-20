from django.urls import path
from .views import *


handler404 = 'store.views.custom_handler404'

urlpatterns = [
    path('accounts/profile/', Profile.as_view(), name='profile'),
    path('accounts/registration/', Registration.as_view(), name='registration'),
    path('license/', license_view, name='license'),
]
