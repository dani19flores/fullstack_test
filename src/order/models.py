import math
import datetime
from django.conf import settings
from django.db import models
from django.db.models import Count, Sum, Q
from django.db.models.signals import post_save, pre_save
from django.core.urlresolvers import reverse
from django.utils import timezone

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
#from eccomerce.utils import unique_order_id_generator
from products.models import products

ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded'),
    ('canceled', 'Canceled'),
    ('completed', 'Completed'),
)

class OrderManagerQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by('-updated', '-timestamp')

    def by_status(self, status='shipped'):
        return self.filter(status=status)

    def not_refunded(self):
        return self.exclude(status='refunded')

    def not_created(self):
        return self.exclude(status='created')

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_recent(self,request):
        return self.get_queryset().by_request(request)

    def new_or_get(self,billing_profile,cart_obj):
        created = False
        qs = self.get_queryset().filter(
            billing_profile__user=billing_profile,
            cart=cart_obj,
            active=True,
            status='created'
        )
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(
                billing_profile__user=billing_profile,
                cart=cart_obj
            )
            created = True
        return obj, created

class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True)
    order_id = models.CharField(max_length=120,blank=True)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True)
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    updated = models.BooleanField(auto_now=True)
    timestamp = models.BooleanField(auto_now_add=True)

    def __str__(self):
        return super().order_id

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp','-updated']

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'order_id':self.order_id})

    def get_status(self):
        if self.status == 'refunded':
            return 'Refunded order'
        elif self.status == 'shipped':
            return 'Shipped'
        return 'Shipping Soon'



