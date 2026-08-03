from decimal import Decimal
import os
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save
def upload_image_path(filepath):
    base_name = os.path.basename(filepath) 
    name, ext = os.path.splitext(base_name)
    return name, ext

class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=20, default=39.99)
    image = models.ImageField(upload_to=upload_image_path, blank=True, null=True)
    feactured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_digital = models.BooleanField(default=False)

    def __str__(self):
        return self.title
