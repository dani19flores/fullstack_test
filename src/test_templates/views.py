import datetime

from django.shortcuts import render

def test_view(request):
    context = {
        "view_title": "Test View",
        "my_number": 42,
        "my_number2": 24,
        "today": datetime.datetime.now().date(),
    }
    template = "test_templates/test_view.html"
    return render(request, template, context)

