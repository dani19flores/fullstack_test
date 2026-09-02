from datetime import datetime

from django.contrib import messages
from django.shortcuts import render

def test_view(request):
    my_list = ["Mouse", "Keyboard", "Monitor", "CPU", "GPU", "RAM", "Motherboard"]
    empty_list = []
    context = {
        "view_title": "Test View",
        "my_number": 42,
        "my_number2": 24,
        "today": datetime.now().date(),
        "my_list": my_list,
        "empty_list": empty_list,
    }
    template = "test_templates/test_view.html"

    messages.add_message(request, messages.INFO, "This is an info message.")
    messages.add_message(request, messages.SUCCESS, "This is a success message.")
    return render(request, template, context)

