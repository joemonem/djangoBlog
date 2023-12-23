from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy, reverse
from .forms import SignUpForm, EditProfileForm
from django.contrib.auth.models import User
from theblog.models import Profile
from django.views.generic import (
    TemplateView,
)
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm

# Create your views here.


class PaymentErrorView(TemplateView):
    template_name = "registration/payment_error.html"


class UserRegistrationView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Access the username of the new user
        username = form.cleaned_data["username"]

        # Retrieve the user object using the username
        user_model = User.objects.get(username=username)

        # Create a Profile object for the new user
        new_profile = Profile.objects.create(user=user_model)
        new_profile.save()

        return response


class UserEditView(generic.UpdateView):
    form_class = EditProfileForm
    template_name = "registration/edit_profile.html"
    success_url = reverse_lazy("custom_login_redirect")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)

        # Access the username of the new user
        username = form.cleaned_data["username"]
        new_bio = form.cleaned_data["bio"]

        # Retrieve the user object using the username
        user_model = User.objects.get(username=username)
        profile_section = Profile.objects.get(user=user_model)

        # Create a Profile object for the new user
        profile_section.bio = new_bio
        profile_section.save()

        return response


class UpdatePassword(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "registration/update_password.html"
    success_url = reverse_lazy("custom_login_redirect")
