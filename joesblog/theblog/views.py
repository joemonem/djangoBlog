from django.shortcuts import render
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
    View,
)
from .models import Post, Profile, Price, Product
from .forms import PostForm, EditForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.views.generic.base import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy, resolve
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


# Payment
import stripe
import os
from django.conf import settings
from django.core.mail import send_mail
from datetime import datetime

from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm

# Pagination
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.


# def home(request):
#     return render(request, "home.html", {})
class HomeView(ListView):
    model = Post
    template_name = "home.html"
    context_object_name = "posts"
    paginate_by = 5  # Adjust the number of posts per page as needed

    # ordering = ["-published_date"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context for user profile
        username = self.kwargs["pk"]
        user_object = get_object_or_404(User, username=username)
        user_profile = get_object_or_404(Profile, user=user_object)

        user_posts = Post.objects.filter(author=user_object)

        following_users = user_profile.following.exclude(username=username)
        following_posts = []

        for profile in following_users:
            following_user_posts = Post.objects.filter(author=profile)
            following_posts.extend(following_user_posts)

        following_posts.sort(key=lambda post: post.id)

        # Paginate user_posts
        user_posts_paginator = Paginator(user_posts, self.paginate_by)
        user_posts_page = self.request.GET.get("user_posts_page")

        try:
            user_posts = user_posts_paginator.page(user_posts_page)
        except PageNotAnInteger:
            user_posts = user_posts_paginator.page(1)
        except EmptyPage:
            user_posts = user_posts_paginator.page(user_posts_paginator.num_pages)

        # Paginate following_posts
        following_posts_paginator = Paginator(following_posts, self.paginate_by)
        following_posts_page = self.request.GET.get("following_posts_page")

        try:
            following_posts = following_posts_paginator.page(following_posts_page)
        except PageNotAnInteger:
            following_posts = following_posts_paginator.page(1)
        except EmptyPage:
            following_posts = following_posts_paginator.page(
                following_posts_paginator.num_pages
            )

        context["user_object"] = user_object
        context["user_profile"] = user_profile
        context["user_posts"] = user_posts
        context["following_posts"] = following_posts

        # Include information about the signed-in user if authenticated
        if self.request.user.is_authenticated:
            current_user_profile = get_object_or_404(Profile, user=self.request.user)
            is_following = current_user_profile.following.filter(
                username=username
            ).exists()

            context["is_following"] = is_following

        return context


@method_decorator(login_required, name="dispatch")
@method_decorator(require_POST, name="post")
class FollowView(View):
    model = Profile

    def post(self, request, *args, **kwargs):
        # Get the current user's profile
        current_user_profile = request.user.id

        # Get the user_id of the user we want to follow
        followee = request.POST.get("followee")

        profile_to_follow = get_object_or_404(Profile, user=followee)
        followee_profile = get_object_or_404(Profile, user=current_user_profile)

        # Check if the current user is already following the user
        is_following = followee_profile.following.filter(
            username=profile_to_follow.user.username
        ).exists()

        if not is_following:
            # If not already following, create the follow relationship
            followee_profile.following.add(profile_to_follow.user)

        # If already following, you might handle it differently (e.g., show an error message)

        return redirect("home", profile_to_follow.user.username)


@method_decorator(login_required, name="dispatch")
@method_decorator(require_POST, name="post")
class UnfollowView(View):
    model = Profile

    def post(self, request, *args, **kwargs):
        # Get the current user's profile
        current_user_profile = request.user.id

        # Get the user_id of the user we want to unfollow
        unfollowee = request.POST.get("unfollowee")

        profile_to_unfollow = get_object_or_404(Profile, user=unfollowee)
        followee_profile = get_object_or_404(Profile, user=current_user_profile)

        # Check if the current user is already following the user
        is_following = followee_profile.following.filter(
            username=profile_to_unfollow.user.username
        ).exists()

        if is_following:
            # If not already following, create the follow relationship
            followee_profile.following.remove(profile_to_unfollow.user)

        return redirect("home", profile_to_unfollow.user.username)


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
        user_object = get_object_or_404(User, username=username)
        user_profile = get_object_or_404(Profile, user=user_object)

        currentTime = int(datetime.now().timestamp())
        validPayment = (currentTime - user_profile.paymentDate) < 31536000

        post_limit_reached = (currentTime - user_profile.last_posted) < 86400

        if validPayment and post_limit_reached is False:
            user_profile.last_posted = currentTime
            user_profile.save()

        return reverse("home", args=[username])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context for user profile
        username = self.request.user.username
        # user_object = User.objects.get(username=username)
        user_object = get_object_or_404(User, username=username)
        user_profile = get_object_or_404(Profile, user=user_object)

        currentTime = int(datetime.now().timestamp())
        validPayment = (currentTime - user_profile.paymentDate) < 31536000

        post_limit_reached = (currentTime - user_profile.last_posted) < 86400

        time_left = int((86400 - (currentTime - user_profile.last_posted)) / 3600)

        print(time_left)

        # if validPayment and post_limit_reached is False:
        #     user_profile.last_posted = currentTime
        #     user_profile.save()

        print(post_limit_reached)

        context["post_limit_reached"] = post_limit_reached
        context["valid_payment"] = validPayment
        context["time_left"] = time_left

        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add additional context for user profile
        username = self.request.user.username
        # user_object = User.objects.get(username=username)
        user_object = get_object_or_404(User, username=username)
        user_profile = get_object_or_404(Profile, user=user_object)

        currentTime = int(datetime.now().timestamp())
        validPayment = (currentTime - user_profile.paymentDate) < 31536000

        context["valid_payment"] = validPayment

        return context


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
            messages.warning(request, f"User '{username}' not found")
            current_url = request.POST.get("current_url")
            current_page_name = resolve(current_url).url_name
            print("Current URL: ", current_url)

            print("Current page name: ", current_page_name)

            if current_page_name == "home":
                # Extract the profile's username, current url at this stage always returns /home/username so 6 skips directly to the username
                extracted_username = current_url[6:]
                redirect_url = reverse("home", args=[extracted_username])
            elif current_page_name == "about":
                redirect_url = reverse(current_page_name)
            # TODO take care of the rest of the cases
            else:
                redirect_url = reverse(current_page_name)

            return redirect(redirect_url)


# Log out
class CustomLoginRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # Get the username of the logged-in user
        username = self.request.user.username

        # Construct the desired URL with the username
        return reverse("home", args=[username])


### Payment ###
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        price = Price.objects.get(id=self.kwargs["pk"])
        domain = "https://yourdomain.com"
        if settings.DEBUG:
            domain = "http://127.0.0.1:8000"
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price.stripe_price_id,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=domain + "/success/",
            cancel_url=domain + "/cancel/",
        )
        return redirect(checkout_session.url)


class SuccessView(TemplateView):
    template_name = "success.html"


class CancelView(TemplateView):
    template_name = "cancel.html"


class ProductLandingPageView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        product = Product.objects.get(name="Test Product")
        prices = Price.objects.filter(product=product)
        context = super(ProductLandingPageView, self).get_context_data(**kwargs)
        context.update({"product": product, "prices": prices})
        return context


class UpdatePassword(PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "update_password.html"
    success_url = reverse_lazy("custom_login_redirect")


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    # Verify that the event is coming from Stripe
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_email = session["customer_details"]["email"]
        payment_date = session["created"]
        payment_intent = session["payment_intent"]

        # Get the user's Profile
        # The first() is no longer necessary since the email is now unique, so more than 1 result is not possible
        user = User.objects.filter(email=customer_email).first()

        # TODO error handling in case user is paying before registering

        profile = Profile.objects.get(user=user)
        profile.paymentDate = payment_date
        profile.save()

        # TODO - send an email to the customer
        # Turns out it costs money to relay emails
        # line_items = stripe.checkout.Session.list_line_items(session["id"])

        # stripe_price_id = line_items["data"][0]["price"]["id"]
        # price = Price.objects.get(stripe_price_id=stripe_price_id)
        # product = price.product

        # send_mail(
        #     subject="Welcome to Thoughboard!",
        #     message=f"Your purchase is much appreciated, you can now create an account. Make sure to register using the email address you used during the payment process!",
        #     recipient_list=[customer_email],
        #     from_email="jmonem@icloud.com",
        # )

    return HttpResponse(status=200)
