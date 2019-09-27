from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import *


class Profile(LoginRequiredMixin, View):
    """Handler for show profile information and edit password and/or email."""

    def get(self, request):
        """GET request. Profile page"""
        edit_form = UserEditForm(request)
        return render(request, "profiles/profile.html", context={'form': edit_form})

    def post(self, request):
        """POST request. Profile page"""
        form = UserEditForm(request.user, request.POST)

        if not form.is_valid():
            return render(request, "profiles/profile.html", context={'form': form})

        form.save()
        update_session_auth_hash(request, form.user)

        return redirect('profile')


class Registration(View):

    def get(self, request):
        """GET request. Registration page"""
        edit_form = UserRegistrationForm()
        return render(request, "profiles/registration.html", context={'form': edit_form})

    def post(self, request):
        """POST request. Registration page

        Return error or register and login new user

        """
        form = UserRegistrationForm(request.POST)

        if not form.is_valid():
            return render(request, "profiles/registration.html", context={'form': form})

        user = form.save()
        login(request, user)

        return redirect('profile')


def license_view(request):
    return render(request, 'profiles/license.html', context={})
