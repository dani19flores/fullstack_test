from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Product

CART_SESSION_KEY = 'cart'


def product_list(request):
    products = Product.objects.all()
    cart = request.session.get(CART_SESSION_KEY, {})
    cart_products = Product.objects.filter(id__in=cart.keys())
    cart_items = [
        {'product': product, 'quantity': cart[str(product.id)]}
        for product in cart_products
    ]
    cart_total = sum(item['product'].price * item['quantity'] for item in cart_items)

    return render(request, 'ventas/ventas.html', {
        'products': products,
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get(CART_SESSION_KEY, {})
    cart[str(product.id)] = cart.get(str(product.id), 0) + 1
    request.session[CART_SESSION_KEY] = cart
    messages.success(request, f"Se agregó '{product.name}' al carrito.")
    return redirect('ventas:product-list')


@require_POST
def process_order(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    if not cart:
        messages.error(request, 'Tu carrito está vacío.')
        return redirect('ventas:product-list')

    request.session[CART_SESSION_KEY] = {}
    messages.success(request, 'Tu pedido fue procesado correctamente.')
    return redirect('ventas:product-list')
