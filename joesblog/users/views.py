from django.shortcuts import render, HttpResponseRedirect
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy, reverse
from .forms import SignUpForm, EditProfileForm
from django.contrib.auth.models import User
from theblog.models import Profile
from .models import Payment
from django.views.generic import (
    TemplateView,
)


# Create your views here.


class PaymentErrorView(TemplateView):
    template_name = "registration/payment_error.html"


# TODO don't let that user to be added into the User database
class UserRegistrationView(generic.CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_invalid(self, form):
        # Access the user's email
        email = form.cleaned_data.get("email", "")

        # If the email isn't found in the Payment model, redirect to the payment error page
        if not Payment.objects.filter(email=email).exists():
            return HttpResponseRedirect(reverse("payment_error"))

        # Call the parent class's form_invalid method for other processing
        return super().form_invalid(form)

    def form_valid(self, form):
        response = super().form_valid(form)

        # Access the user's email
        email = form.cleaned_data["email"]

        # If the email isn't found in the Payment model, I want to display the error page and break off the rest of the code
        if not Payment.objects.filter(email=email).exists():
            return HttpResponseRedirect(reverse("payment_error"))

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
