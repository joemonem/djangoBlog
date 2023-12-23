# Generated by Django 4.2.7 on 2023-12-09 21:26

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("theblog", "0012_alter_profile_following"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="following",
            field=models.ManyToManyField(
                related_name="followers", to=settings.AUTH_USER_MODEL
            ),
        ),
    ]