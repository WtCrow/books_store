from django.views.generic import View
from .forms import *
from django.shortcuts import render, redirect
from django.contrib.auth import login, update_session_auth_hash


class EditProfile(View):

    def get(self, request):
        edit_form = UserEditForm(request)
        return render(request, "profiles/profile.html", context={'form': edit_form})

    def post(self, request):
        form = UserEditForm(request.user, request.POST)

        if not form.is_valid():
            return render(request, "profiles/profile.html", context={'form': form})

        form.save()
        update_session_auth_hash(request, form.user)

        return redirect('profile')


class Registration(View):

    def get(self, request):
        edit_form = UserRegistrationForm()
        return render(request, "profiles/registration.html", context={'form': edit_form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)

        if not form.is_valid():
            return render(request, "profiles/registration.html", context={'form': form})

        user = form.save()
        login(request, user)

        return redirect('profile')
