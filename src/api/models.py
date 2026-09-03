from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class Product(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)