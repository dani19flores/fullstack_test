import datetime

from django.shortcuts import render

def test_view(request):
    my_list = ["Mouse", "Keyboard", "Monitor", "CPU", "GPU", "RAM", "Motherboard"]
    empty_list = []
    context = {
        "view_title": "Test View",
        "my_number": 42,
        "my_number2": 24,
        "today": datetime.datetime.now().date(),
        "my_list": my_list,
        "empty_list": empty_list,
    }
    template = "test_templates/test_view.html"
    return render(request, template, context)

