from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from ckeditor.fields import RichTextField

User._meta.get_field("email")._unique = True


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # This held a basic text field
    # body = models.TextField(null=True)

    body = RichTextField(blank=True, null=True)
    # body = BleachField(blank=True, null=True)

    published_date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        # return reverse("article-details", args=(str(self.id)))
        return reverse("home")


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, max_length=1000)
    paymentDate = models.IntegerField(default=0)
    following = models.ManyToManyField(User, related_name="following", default=list())

    def __str__(self):
        return self.user.username


# Payment


class Product(models.Model):
    name = models.CharField(max_length=100)
    stripe_product_id = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Price(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stripe_price_id = models.CharField(max_length=100)
    price = models.IntegerField(default=0)  # cents

    def get_display_price(self):
        return "{0:.2f}".format(self.price / 100)
