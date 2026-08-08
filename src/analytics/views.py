from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.http.request import HttpRequest
from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.utils import timezone
from order.models import Order

class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.is_staff:
            qs = Order.objects.all().by_week_data(week_ago=5, number_of_weeks=5)
            if request.GET.get('type') == 'week':
                days = 7
                start_date = timezone.now() - timedelta(days=days-1)
                datetime_list = []
                labels = []
                sales_items = []
                for x in range(0,days):
                    new_time = start_date + timedelta(days=x)
                    datetime_list.append(new_time)
                    labels.append(new_time.strftime('%a'))
                    new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
                    day_total = new_qs.total_data()['total__sum'] or 0
                    sales_items.append(day_total)
                data['labels'] = labels
                data['data'] = sales_items
        return JsonResponse(data)

class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self,  *args, **kwargs):
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        qs = Order.objects.all()
        context['orders'] = qs
        context['recent_orders'] = qs.recent().not_refunded()[:5]
        context['shipped_orders'] = qs.recent().not_refunded().by_status(status='shipped')[:5]
        context['paid_orders'] = qs.recent().not_refunded().by_status(status='paid')[:5]
        print(context)
        return context