from django.urls import path
from .views import *


urlpatterns = [
    path('profile/', Profile.as_view(), name='profile'),
    path('registration/', Registration.as_view(), name='registration'),
    path('license/', license_view, name='license'),
]
