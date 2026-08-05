from django.contrib import admin
from .models import User, GuestEmail

admin.site.register(User)
admin.site.register(GuestEmail)
