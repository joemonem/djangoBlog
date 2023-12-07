from django.db import models

# Create your models here.


class Payment(models.Model):
    email = models.EmailField(max_length=100)
    paymentDate = models.IntegerField()

    def __str__(self):
        return self.email
