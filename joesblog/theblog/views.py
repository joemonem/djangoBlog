from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from .models import Post, Profile
from .forms import PostForm, EditForm
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
import random

# Create your views here.


# def home(request):
#     return render(request, "home.html", {})
class HomeView(ListView):
    model = Post
    template_name = "home.html"
    context_object_name = "posts"
    ordering = ["-published_date"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context for user profile
        username = self.kwargs["pk"]
        user_object = User.objects.get(username=username)
        user_profile = Profile.objects.get(user=user_object)
        user_posts = Post.objects.filter(author=user_object)

        context["user_object"] = user_object
        context["user_profile"] = user_profile
        context["user_posts"] = user_posts

        return context


class AboutView(TemplateView):
    template_name = "about.html"


class ArticleDetailsView(DetailView):
    model = Post
    template_name = "article_details.html"


class AddPostView(CreateView):
    model = Post
    template_name = "add_post.html"
    form_class = PostForm
    # fields = "__all__"
    # fields = ("title", "author", "body")


class UpdatePostView(UpdateView):
    model = Post
    template_name = "update_post.html"
    form_class = EditForm


class DeletePostView(DeleteView):
    model = Post
    template_name = "delete_post.html"
    success_url = reverse_lazy("home")
