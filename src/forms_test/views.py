from django.shortcuts import render
from .forms import TestForm

def home(request):
    initial_data = {
        "some_text":"Texto inicial",
        #"bolean": True,
        #"integer": 10,
        #"email": "example@example.com"
        #"option": "option1"
        #"radio_option": "radio1"
    }
    form = TestForm(request.POST or None, initial=initial_data)
    if form.is_valid():
        print(form.cleaned_data)
    return render(request, 'forms.html', {'form': form})
