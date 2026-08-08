import math
import datetime
from django.conf import settings
from django.db import models
from django.db.models import Avg, Count, Sum, Q
from django.db.models.signals import post_save, pre_save
from django.urls import reverse
from django.utils import timezone

from addresses.models import Address
from billing.models import BillingProfile
from carts.models import Cart
#from eccomerce.utils import unique_order_id_generator

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

    def get_sales_breakdown(self):
        recent = self.recent().not_refunded()
        recent_data = recent.total_data()
        recent_cart_data = recent.cart_data()
        shipped = recent.by_status(status='shipped')
        shipped_data = shipped.totals_data()
        paid = recent.by_status(status='paid')
        paid_data = paid.total_data()
        data = {
            "recent":recent,
            "recent_data":recent_data,
            "recent_cart_data":recent_cart_data,
            "shipped":shipped,
            "shipped_data":shipped_data,
            "paid":paid,
            "paid_data":paid_data,
        }
        return data

    def by_status(self, status='shipped'):
        return self.filter(status=status)

    def not_refunded(self):
        return self.exclude(status='refunded')

    def not_created(self):
        return self.exclude(status='created')

    def by_request(self, start_date, end_date=None):
        if end_date is None:
            return self.filter(updated__gte=start_date)
        return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

    def total_data(self):
        return self.aggregate(Sum('total'), Avg('total'))

    def by_week_data(self, week_ago=7, number_of_weeks=2):
        if number_of_weeks > week_ago:
            number_of_weeks = week_ago
        days_ago_start = week_ago * 7
        days_ago_end = days_ago_start - (number_of_weeks * 7)
        start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
        end_date = timezone.now() - datetime.timedelta(days=days_ago_end)
        return self.by_request(start_date, end_date)

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
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True, on_delete=models.CASCADE)
    order_id = models.CharField(max_length=120,blank=True)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True, on_delete=models.CASCADE)
    billing_address = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id or str(self.pk)

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



