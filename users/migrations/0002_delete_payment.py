# Generated by Django 4.2.7 on 2023-12-08 09:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Payment",
        ),
    ]
