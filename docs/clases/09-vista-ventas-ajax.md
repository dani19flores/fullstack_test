# Clase: Crea la vista de ventas con Ajax

## Temas cubiertos en la clase

- Implementar la validación de usuario staff en la vista.
- Filtrar y mostrar datos de ventas actualizados en la semana.
- Desarrollar la integración de Ajax para actualización dinámica de la vista
  de ventas.

## Contexto

Esta clase agrega una segunda vista a `analytics` — `SalesAjaxView` — que
expone los datos de ventas como JSON, para que el frontend (jQuery + Chart.js,
ver [clase 08](08-frontend-graficas-chartjs.md)) pueda pedirlos por Ajax y
dibujar la gráfica sin recargar la página.

```
src/analytics/views.py       -> nueva clase SalesAjaxView
src/analytics/urls.py        -> nueva ruta /analytics/sales/data
src/order/models.py          -> by_week_data ahora se apoya en by_request
src/templates/analytics/sales.html -> script que consume el endpoint
```

## 1. Validación de usuario staff en la vista

```python
class SalesAjaxView(View):
    def get(self, request, *args, **kwargs):
        data = {}
        if request.user.is_staff:
            ...
        return JsonResponse(data)
```

A diferencia de `SalesView` (que corta el acceso devolviendo un
`HttpResponse('Unauthorized', status=401)` desde `dispatch()`, ver
[clase 02](02-extiende-clases-base-vistas.md)), `SalesAjaxView` valida
`request.user.is_staff` **dentro** de `get()`, envolviendo toda la lógica en
un `if`. Si el usuario no es staff, `data` se queda como diccionario vacío
`{}` y la vista responde `JsonResponse({})` con `200 OK` — no hay error, pero
tampoco datos. Es una validación más permisiva que la de `SalesView` (no
bloquea con 401, simplemente no entrega información).

`SalesAjaxView` hereda de `View` (la clase base genérica de Django, sin
mixins de autenticación) en vez de usar `LoginRequiredMixin` como `SalesView`
— por eso la validación de staff se hace a mano en vez de delegarla a un
mixin.

## 2. Filtrar y mostrar datos de ventas de la semana

```python
qs = Order.objects.all().by_week_data(week_ago=5, number_of_weeks=5)
if request.GET.get('type') == 'week':
    days = 7
    start_date = timezone.now() - timedelta(days=days-1)
    labels = []
    sales_items = []
    for x in range(0, days):
        new_time = start_date + timedelta(days=x)
        labels.append(new_time.strftime('%a'))
        new_qs = qs.filter(updated__day=new_time.day, updated__month=new_time.month)
        day_total = new_qs.total_data()['total__sum'] or 0
        sales_items.append(day_total)
    data['labels'] = labels
    data['data'] = sales_items
```

- **`request.GET.get('type')`**: el endpoint acepta un parámetro de query
  (`?type=week`) para decidir qué agregación devolver — hoy solo está
  implementado el caso `'week'`; cualquier otro valor devuelve `{}`.
- **`by_week_data(week_ago=5, number_of_weeks=5)`**: método de
  `OrderManagerQuerySet` (clase 08) que calcula un rango de fechas y delega en
  `by_request(start_date, end_date)` para filtrar `Order` por `updated` dentro
  de ese rango.
- **Bucle de 7 días**: arranca en `start_date` (hoy menos 6 días) y avanza
  día por día hasta hoy, armando dos listas en paralelo:
  - `labels`: el nombre corto del día (`'%a'` → "Mon", "Tue", ...).
  - `sales_items`: el total vendido *ese día específico*, calculado
    filtrando `qs` por `updated__day` y `updated__month` y agregando con
    `total_data()['total__sum']` (si no hay ventas ese día, `total__sum` es
    `None`, de ahí el `or 0` para no romper la gráfica con `null`).
- El resultado queda en `data['labels']` (eje X) y `data['data']` (eje Y) —
  exactamente el formato que espera Chart.js del lado del frontend.

## 3. Integración de Ajax para actualización dinámica

En [`src/templates/analytics/sales.html`](../../src/templates/analytics/sales.html):

```javascript
$(document).ready(function(){
    function renderChart(id, data, labels){
        var ctx = $('#'+id)
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{ label: labels, data: data, borderWidth: 1 }]
            },
            options: { scales: { y: { beginAtZero: true } } }
        });
    }

    function getSalesData(id, type){
        $.ajax({
            url: '/analytics/sales/data',
            method: 'GET',
            data: {'type': type},
            success: function(responseData){
                renderChart(id, responseData.data, responseData.labels)
            },
            error: function(error_data){
                console.log('error')
                console.log(error_data)
            }
        })
    }

    var chartsToRender = $('.render-chart')
    $.each(chartsToRender, function(index, html){
        var $this = $(this)
        if ($this.attr('id') && $this.attr('data-type')){
            getSalesData($this.attr('id'), $this.attr('data-type'))
        }
    })
})
```

Con el `<canvas>` correspondiente en el `content` del template:

```html
<canvas class="render-chart" id="thisWeekSales" data-type="week" width="400" height="400"></canvas>
```

El patrón es genérico a propósito, para poder soportar varias gráficas en la
misma página sin repetir código:

1. Al cargar el DOM (`$(document).ready`), se buscan **todos** los elementos
   con la clase `.render-chart` (hoy solo hay uno, `thisWeekSales`, pero el
   código no está atado a un único `id`).
2. Por cada uno, si tiene `id` y `data-type`, se llama a `getSalesData(id, type)`
   — el `data-type="week"` del HTML es justo lo que llega como `?type=week`
   al endpoint.
3. `getSalesData` hace la petición Ajax (`$.ajax`) a `/analytics/sales/data`.
   Si responde con éxito, `renderChart` toma `responseData.labels` y
   `responseData.data` — el mismo diccionario que arma `SalesAjaxView` — y
   los usa para instanciar el `Chart` de Chart.js sobre el `<canvas>` con ese
   `id`.
4. Si la petición falla, el `error` callback solo hace `console.log` (no
   muestra nada al usuario en pantalla, útil para depurar en dev, no para
   producción).

Este es el mecanismo de "actualización dinámica": la gráfica no se calcula en
el servidor al renderizar `sales.html` (como sí pasa con `recent_orders`,
`shipped_orders`, `paid_orders`, que llegan listos en el contexto — clase 07),
sino que el navegador la pide aparte, después de que la página ya cargó, sin
necesidad de recargarla.

## Cómo se llenaron los datos de prueba

Como el proyecto no tenía ninguna orden todavía, se sembraron datos manuales
para poder ver la vista y la gráfica funcionando (no forman parte del código
de la app, solo se ejecutaron una vez desde `manage.py shell`):

```python
from carts.models import Cart
from order.models import Order
from decimal import Decimal

cart = Cart.objects.create(subtotal=Decimal('50.00'), total=Decimal('55.99'))

data = [
    ('created', Decimal('55.99')),
    ('paid', Decimal('29.99')),
    ('paid', Decimal('120.50')),
    ('shipped', Decimal('75.00')),
    ('shipped', Decimal('45.25')),
    ('completed', Decimal('89.99')),
]
for status, total in data:
    Order.objects.create(cart=cart, status=status, total=total, shipping_total=Decimal('5.99'))
```

Puntos a tener en cuenta sobre este *seed*:

- `Order.cart` es un `ForeignKey` **obligatorio** (`on_delete=models.CASCADE`,
  sin `null=True`) — no se puede crear una orden sin un `Cart` existente, por
  eso primero se crea uno.
- `billing_profile`, `shipping_address` y `billing_address` sí son
  `null=True, blank=True`, así que se pudieron omitir para estos datos de
  prueba.
- `updated` y `timestamp` son `auto_now`/`auto_now_add` — Django los llena
  solos con la fecha/hora actual al guardar; no se pueden pasar a mano en
  `create()` (por eso todas las órdenes de prueba quedaron con fecha de hoy,
  lo cual conviene para que aparezcan en el filtro "de esta semana").
- Se usaron distintos `status` (`created`, `paid`, `shipped`, `completed`)
  para que las tres columnas de `SalesView` (Recientes/Enviados/Pagados)
  tuvieran contenido para mostrar.

## Estado actual del código (pendiente de completar)

1. **`order_id` queda vacío** en todas las órdenes: nada lo genera todavía.
   La señal `pre_save` con `unique_order_id_generator` (preparada desde la
   [clase 05](05-modelos-ordenes-django.md)) sigue comentada
   (`#from eccomerce.utils import unique_order_id_generator`), así que
   `{{ order.order_id }}` se ve vacío en el template.
2. **`get_sales_breakdown()` sigue sin usarse y sigue rota** (llama a
   `cart_data()`, que no existe, y a `totals_data()`, con el mismo typo que
   ya se corrigió en `SalesAjaxView` pero no aquí) — quedó como código muerto
   desde la clase 08, ninguna vista la llama.
3. **`OrderManager.by_recent(self, request)`** sigue llamando a
   `self.get_queryset().by_request(request)`, pero `by_request` ahora espera
   `(start_date, end_date=None)`, no un objeto `request` de Django — mismo
   pendiente señalado en clases anteriores.
4. **Sin manejo de error visible para el usuario**: si el `$.ajax` falla, el
   `<canvas>` se queda vacío sin ningún mensaje en pantalla (solo
   `console.log`).
5. Sigue presente el `print(context)` de depuración en
   `SalesView.get_context_data` (clase 07).

## Próximos pasos sugeridos

- Conectar la señal `pre_save` de `Order` para generar `order_id`
  automáticamente.
- Eliminar o terminar de corregir `get_sales_breakdown()` si se va a usar en
  algún momento; si no, quitarlo para no dejar código muerto.
- Revisar `OrderManager.by_recent` a la luz del nuevo `by_request(start_date, end_date)`.
- Agregar retroalimentación visual (mensaje de error) cuando falla la
  petición Ajax.
