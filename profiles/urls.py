from django.urls import path
from .views import *


handler404 = 'store.views.custom_handler404'

urlpatterns = [
    path('accounts/profile/', EditProfile.as_view(), name='profile'),
    path('registration/', Registration.as_view(), name='registration')
]
