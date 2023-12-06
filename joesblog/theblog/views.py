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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages

# Create your views here.


# def home(request):
#     return render(request, "home.html", {})
class HomeView(ListView):
    model = Post
    template_name = "home.html"
    context_object_name = "posts"
    # ordering = ["-published_date"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context for user profile
        username = self.kwargs["pk"]
        # user_object = User.objects.get(username=username)
        user_object = get_object_or_404(User, username=username)
        user_profile = get_object_or_404(Profile, user=user_object)

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

    def get_success_url(self):
        username = self.request.user.username
        return reverse("home", args=[username])

    # fields = "__all__"
    # fields = ("title", "author", "body")


class UpdatePostView(UpdateView):
    model = Post
    template_name = "update_post.html"
    form_class = EditForm

    def get_success_url(self):
        username = self.request.user.username
        article = self.object.pk
        return reverse("article-details", args=[article])


class DeletePostView(DeleteView):
    model = Post
    template_name = "delete_post.html"

    def get_success_url(self):
        username = self.request.user.username
        return reverse("home", args=[username])


# Search
class SearchRedirectView(RedirectView):
    def post(self, request, *args, **kwargs):
        # Access the user's submission
        username = request.POST.get("username", "")

        try:
            # Check if the user with the given username exists
            User.objects.get(username=username)

            # Construct the desired URL with the username
            redirect_url = reverse("home", args=[username])

            # Redirect to the constructed URL
            return redirect(redirect_url)

        except User.DoesNotExist:
            # Handle the case where the user is not found
            messages.warning(request, f"User '{username}' not found.")
            current_url = self.request.path
            print(current_url)
            return render(request, "home.html", {"current_url": current_url})


# Log out
class CustomLoginRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # Get the username of the logged-in user
        username = self.request.user.username

        # Construct the desired URL with the username
        return reverse("home", args=[username])
