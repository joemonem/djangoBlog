"""
URL configuration for joesblog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import (
    HomeView,
    ArticleDetailsView,
    AddPostView,
    UpdatePostView,
    DeletePostView,
    AboutView,
    CustomLoginRedirectView,
    SearchRedirectView,
    CreateCheckoutSessionView,
    SuccessView,
    CancelView,
    ProductLandingPageView,
)


# urlpatterns = [path("", views.home, name="home")]
urlpatterns = [
    path("", AboutView.as_view(), name="about"),
    path("home/<str:pk>", HomeView.as_view(), name="home"),
    path(
        "custom_login_redirect/",
        CustomLoginRedirectView.as_view(),
        name="custom_login_redirect",
    ),
    path(
        "search_redirect",
        SearchRedirectView.as_view(),
        name="search_redirect",
    ),
    path("addpost", AddPostView.as_view(), name="addpost"),
    path("article/<int:pk>", ArticleDetailsView.as_view(), name="article-details"),
    path("article/edit/<int:pk>", UpdatePostView.as_view(), name="update_post"),
    path("article/<int:pk>/delete", DeletePostView.as_view(), name="delete_post"),
    # Payment
    path("cancel/", CancelView.as_view(), name="cancel"),
    path("success/", SuccessView.as_view(), name="success"),
    path(
        "create-checkout-session/<pk>/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("landing", ProductLandingPageView.as_view(), name="landing"),
]
