from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django import forms
from theblog.models import Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )


class EditProfileForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    username = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=50, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    bio = forms.CharField(
        max_length=1000,
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password", "bio")

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     # Set the initial value for the bio field
    #     if self.instance:
    #         # Access the profile from the user instance
    #         profile_section = self.instance.profile

    #         self.fields["bio"].initial = profile_section.bio
