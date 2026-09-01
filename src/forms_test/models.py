from django.db import models
from django.conf import settings

class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)