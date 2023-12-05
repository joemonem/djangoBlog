from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from ckeditor.fields import RichTextField

# from django_bleach.models import BleachField


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
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username
