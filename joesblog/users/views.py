from django.shortcuts import render
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.urls import reverse_lazy
from .forms import SignUpForm
from django.contrib.auth.models import User
from theblog.models import Profile
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse


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
    form_class = UserChangeForm
    template_name = "registration/edit_profile.html"
    success_url = reverse_lazy("home")

    def get_object(self):
        return self.request.user


# Log out
class CustomLoginRedirectView(LoginRequiredMixin, RedirectView):
    pattern_name = "home_with_username"

    def get_redirect_url(self, *args, **kwargs):
        # Get the username of the logged-in user
        username = self.request.user.username

        # Construct the desired URL with the username
        return reverse(self.pattern_name, args=[username])
