from django.shortcuts import render
from django.forms import modelformset_factory

from .forms import ProductModelForm
from .models import Product


def home(request):
    ProductModelFormSet = modelformset_factory(Product, form=ProductModelForm)
    formset = ProductModelFormSet(request.POST or None, queryset=Product.objects.all())

    print("formset.data")
    print(formset.data)

    print("formset.errors")
    print(formset.errors)

    if formset.is_valid():
        print("ModelFormSet is valid")
        formset.save()

    context = {
        'formset': formset
    }
    
    return render(request, 'formset_view.html', context)
