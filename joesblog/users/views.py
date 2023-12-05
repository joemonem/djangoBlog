from django.shortcuts import render
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from .forms import SignUpForm, EditProfileForm
from django.contrib.auth.models import User
from theblog.models import Profile


# Create your views here.
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
