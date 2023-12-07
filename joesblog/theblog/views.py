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
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

# Payment
import stripe
import os
from django.conf import settings
from users.models import Payment
from django.core.mail import send_mail


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

        # Load instance of payment model
        payment = Payment()

        # Save user's email in the Payment model
        payment.email = customer_email

        # Save user's payment date in the Payment model
        payment.paymentDate = payment_date

        payment.save()

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
