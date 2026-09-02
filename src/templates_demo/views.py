from django.shortcuts import render


def page(request):
    products = [
        {"name": "Mouse", "price": 19.99},
        {"name": "Keyboard", "price": 45.50},
        {"name": "Monitor", "price": 199.00},
        {"name": "CPU", "price": 320.00},
        {"name": "GPU", "price": 780.00},
        {"name": "RAM", "price": 89.90},
        {"name": "Motherboard", "price": 150.00},
    ]
    total = sum(p["price"] for p in products)
    context = {
        "headline": "  bienvenido al módulo de templates de django  ",
        "divisible_by": 2,
        "products": products,
        "total_products": len(products),
        "total_price": total,
        "average_price": total / len(products),
    }
    return render(request, "templates_demo/page.html", context)
