from django.shortcuts import render
from .forms import TestForm

def home(request):
    form = TestForm(request.POST or None)
    if form.is_valid():
        print(form.cleaned_data)
    return render(request, 'forms.html', {'form': form})
