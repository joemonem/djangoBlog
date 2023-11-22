from django.urls import path
from .views import UserRegistrationView, UserEditView

urlpatterns = [
    path("signup/", UserRegistrationView.as_view(), name="signup"),
    path("edit_profile/", UserEditView.as_view(), name="edit_profile"),
]
