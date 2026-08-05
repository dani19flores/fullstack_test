# Clase: Modifica el get_context_data en las views y crea el Order model

## Temas cubiertos en la clase

- Modificar el método `get_context_data` en las views para utilizar un
  diccionario como contexto.
- Importar el modelo `Order` y utilizarlo para crear un queryset.
- Crear diferentes llaves en el diccionario de contexto para mostrar órdenes
  recientes, enviadas y pagadas.

## Contexto

Esta clase conecta `analytics.SalesView` (creada en la
[clase 02](02-extiende-clases-base-vistas.md)) con el modelo `Order`
(definido en la [clase 05](05-modelos-ordenes-django.md) y completado con sus
dependencias en la [clase 06](06-modelos-billing-cart-product.md)), para que
la página de ventas muestre datos reales de órdenes en vez de estar vacía.

Archivos tocados:

```
modificado: src/analytics/views.py
modificado: src/templates/analytics/sales.html
modificado: src/config/settings.py
modificado: src/order/models.py
```

## 1. `get_context_data` con un diccionario de contexto

```python
class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(SalesView, self).get_context_data(*args, **kwargs)
        qs = Order.objects.all()
        context['orders'] = qs
        context['recent_orders'] = qs.recent().not_refunded()[:5]
        context['shipped_orders'] = qs.recent().not_refunded().by_status(status='shipped')[:5]
        context['paid_orders'] = qs.recent().not_refunded().by_status(status='paid')[:5]
        print(context)
        return context
```

Antes, `get_context_data` solo llamaba a `super()` y devolvía el contexto tal
cual (sin agregar nada). Ahora:

- Se guarda el resultado de `super().get_context_data(*args, **kwargs)` en
  `context` — que en Django **siempre es un diccionario** (`dict`), aunque no
  se note hasta que empiezas a agregarle llaves nuevas como se hace aquí.
- Se le agregan llaves nuevas (`context['orders'] = ...`, etc.) igual que a
  cualquier diccionario de Python. Cada llave queda disponible en el template
  con ese mismo nombre (`{% for order in recent_orders %}`).
- Al final se devuelve `context`, ya con las llaves nuevas, para que
  `TemplateView` lo use al renderizar `sales.html`.

## 2. Importar `Order` y construir un queryset

```python
from order.models import Order
...
qs = Order.objects.all()
```

`Order.objects` es el `OrderManager` personalizado definido en la
[clase 05](05-modelos-ordenes-django.md) — `Order.objects.all()` devuelve un
`OrderManagerQuerySet` (no un `QuerySet` genérico), por lo que a partir de ahí
se pueden encadenar los métodos custom del manager: `.recent()`,
`.not_refunded()`, `.by_status()`.

## 3. Llaves del contexto: recientes, enviadas y pagadas

```python
context['recent_orders'] = qs.recent().not_refunded()[:5]
context['shipped_orders'] = qs.recent().not_refunded().by_status(status='shipped')[:5]
context['paid_orders'] = qs.recent().not_refunded().by_status(status='paid')[:5]
```

Las tres llaves comparten la misma base (`recent()` para ordenar por más
reciente, `not_refunded()` para descartar órdenes reembolsadas) y solo varían
en el filtro adicional:

- **`recent_orders`**: las 5 órdenes no reembolsadas más recientes, sin
  filtrar por estado.
- **`shipped_orders`**: de esas, solo las que están en estado `shipped`.
- **`paid_orders`**: de esas, solo las que están en estado `paid`.

El `[:5]` al final de cada queryset limita el resultado a 5 registros (Django
traduce el *slice* en un `LIMIT` a nivel de SQL, no trae todo y luego recorta
en Python).

En [`src/templates/analytics/sales.html`](../../src/templates/analytics/sales.html)
se agregaron tres bloques (uno por cada llave) que iteran el queryset
correspondiente y muestran `order_id`, `total` y `updated`, con un mensaje
`{% empty %}` para cuando no hay órdenes en esa categoría — así la página no
se rompe ni se ve vacía sin explicación mientras no haya datos.

## Estado actual del código (pendiente de completar)

1. **`INSTALLED_APPS` apunta a una app que no existe**: se agregó
   `"orders.apps.OrdersConfig"` (plural) en
   [`src/config/settings.py`](../../src/config/settings.py), pero la carpeta
   real es `src/order/` (singular) con la clase `OrderConfig` en
   [`src/order/apps.py`](../../src/order/apps.py). Con este mismatch, Django
   no va a poder arrancar (`ModuleNotFoundError: No module named 'orders'`).
   Debería decir `"order.apps.OrderConfig"`.
2. **`order/models.py` sigue con un import roto**:
   `from products.models import products` — el módulo `products.models`
   define la clase `Product` (mayúscula), no un nombre `products`. En cuanto
   se corrija el punto anterior y Django intente cargar `order`, este import
   va a fallar también.
3. **`print(context)` de depuración** quedó en `get_context_data` — imprime
   el contexto completo (incluye los querysets) en la consola del servidor en
   cada request a `/analytics/sales`. Conviene quitarlo antes de dar la clase
   por cerrada.
4. Siguen pendientes los bugs ya señalados en la
   [clase 05](05-modelos-ordenes-django.md) sobre `order/models.py`:
   `__str__` (`super().order_id` en vez de `self.order_id`),
   `OrderManager.by_recent` (llama a `by_request`, que no existe), y
   `new_or_get` (mezcla `billing_profile__user=` con `.create()`).
5. **Sin migraciones para `order`** — aunque el resto de apps
   (`addresses`, `billing`, `carts`, `products`) ya están en
   `INSTALLED_APPS`, no se confirmó que tengan sus migraciones generadas y
   aplicadas, necesarias para que `Order.objects.all()` pueda ejecutar una
   consulta real contra la base de datos.

## Próximos pasos sugeridos

- Corregir `"orders.apps.OrdersConfig"` → `"order.apps.OrderConfig"` en
  `INSTALLED_APPS`.
- Corregir el import `from products.models import products` →
  `from products.models import Product` (y revisar si `Order` realmente
  necesita usar `Product` directamente, o si ese import sobra).
- Quitar el `print(context)`.
- Generar y aplicar migraciones para todas las apps nuevas, y probar
  `/analytics/sales` con datos reales.
