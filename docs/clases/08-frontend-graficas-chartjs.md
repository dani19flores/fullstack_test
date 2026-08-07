# Clase: Integra el Frontend para visualizar las ventas en gráficas

## Temas cubiertos en la clase

- Instalar Chart.js para representar datos de ventas en el frontend.
- Modificar modelos para obtener datos dinámicos de ventas.
- Integrar gráficos interactivos en las vistas del proyecto.

## Contexto

Esta clase le agrega una capa visual (gráfica de barras) a
`analytics.SalesView` (clases [02](02-extiende-clases-base-vistas.md),
[07](07-context-data-order-model.md)), y empieza a preparar el modelo
`Order` para poder alimentar esa gráfica con datos reales en vez de números
fijos. Archivos tocados:

```
nuevo:       package.json (+ node_modules/, sin trackear)
modificado:  src/templates/base/js.html
modificado:  src/templates/analytics/sales.html
modificado:  src/order/models.py
```

## 1. Instalar Chart.js

Se corrió `npm install chart.js`, lo que generó
[`package.json`](../../package.json):

```json
{
  "dependencies": {
    "chart.js": "^4.5.1"
  }
}
```

Sin embargo, la librería **no se está usando desde ese paquete de npm** — en
la práctica se cargó por CDN en dos lugares distintos:

- [`src/templates/base/js.html`](../../src/templates/base/js.html) (el
  parcial global que se incluye en `layouts/base.html`, o sea en **todas**
  las páginas del sitio):
  ```html
  {% load static %}
  <!-- Chart.js -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.0/chart.min.js"></script>
  <script src="{% static 'js/app.js' %}"></script>
  ```
- [`src/templates/analytics/sales.html`](../../src/templates/analytics/sales.html),
  que carga **otra vez** Chart.js, desde un CDN distinto (jsdelivr en vez de
  cdnjs), justo antes de usarlo.

## 2. Modificar modelos para obtener datos dinámicos de ventas

En [`src/order/models.py`](../../src/order/models.py) se amplió
`OrderManagerQuerySet` con métodos pensados para alimentar la gráfica con
datos agregados (sumas/promedios) en vez de listas crudas de órdenes:

```python
from django.db.models import Avg, Count, Sum, Q
...

def get_sales_breakdown(self):
    recent = self.recent().not_refunded()
    recent_data = recent.total_data()
    recent_cart_data = recent.cart_data()
    shipped = recent.by_status(status='shipped')
    shipped_data = shipped.totals_data()
    paid = recent.by_status(status='paid')
    paid_data = paid.total_data()
    data = {
        "recent": recent,
        "recent_data": recent_data,
        "recent_cart_data": recent_cart_data,
        "shipped": shipped,
        "shipped_data": shipped_data,
        "paid": paid,
        "paid_data": paid_data,
    }
    return data

def by_request(self, start_date, end_date=None):
    if end_date is None:
        return self.filter(updated__gte=start_date)
    return self.filter(updated__gte=start_date).filter(updated__lte=end_date)

def total_data(self):
    return self.aggregate(Sum('total'), Avg('total'))

def by_week_data(self, week_ago=7, number_of_weeks=2):
    if number_of_weeks > week_ago:
        number_of_weeks = week_ago
    days_ago_start = week_ago * 7
    days_ago_end = days_ago_start - (number_of_weeks * 7)
    start_date = timezone.now() - datetime.timedelta(days=days_ago_start)
    end_date = timezone.now() - datetime.timedelta(days=days_ago_end)
    return self.by_range(start_date, end_date)
```

- **`total_data()`**: usa `.aggregate(Sum('total'), Avg('total'))` — en vez de
  devolver una lista de órdenes, devuelve un diccionario con la suma y el
  promedio de `total` sobre el queryset actual (`{'total__sum': ..., 'total__avg': ...}`).
  Es el tipo de dato que una gráfica necesita (un número, no un listado).
- **`by_request(start_date, end_date=None)`**: filtra órdenes por rango de
  fechas sobre `updated`. Reemplaza la idea original de "por request" (de la
  clase 05) por un filtro explícito de fechas.
- **`by_week_data(week_ago, number_of_weeks)`**: calcula un rango de fechas
  (por ejemplo, "las órdenes de hace 2 semanas hasta hace 1 semana") usando
  `timezone.now()` y `datetime.timedelta`, pensado para alimentar
  comparativas semana a semana en la gráfica.
- **`get_sales_breakdown()`**: junta todo lo anterior en un solo diccionario
  con las órdenes recientes/enviadas/pagadas *y* sus totales agregados, listo
  en teoría para pasarlo al contexto de la vista y de ahí al `<script>` de
  Chart.js.

## 3. Integrar gráficos interactivos en las vistas

En [`src/templates/analytics/sales.html`](../../src/templates/analytics/sales.html)
se agregó un bloque `{% block javascript %}` (uno de los tres puntos de
extensión que define `layouts/base.html`, ver
[clase 02](02-extiende-clases-base-vistas.md)):

```html
{% block javascript %}
    <div>
        <canvas id="myChart"></canvas>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <script>
        const ctx = document.getElementById('myChart');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'],
                datasets: [{
                    label: 'Ventas',
                    data: [12, 19, 3, 5, 2, 3],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>
{% endblock %}
```

- **`<canvas id="myChart">`**: Chart.js dibuja sobre un elemento `<canvas>`;
  necesita un `id` para que el script lo encuentre con
  `document.getElementById`.
- **`new Chart(ctx, {...})`**: la API de Chart.js — `type: 'bar'` (gráfica de
  barras), `data.labels` (eje X) y `data.datasets[0].data` (los valores),
  más `options.scales.y.beginAtZero` para que el eje Y siempre arranque en 0
  (evita gráficas engañosas que no parten de cero).
- **Estado actual: datos fijos, no dinámicos.** `labels` y `data` están
  escritos a mano (`['Lunes', ...]`, `[12, 19, 3, 5, 2, 3]`) — es una gráfica
  de ejemplo para probar que Chart.js funciona, todavía **no** consume nada
  de `get_sales_breakdown()` ni de ningún dato real de `Order`.

## Estado actual del código (pendiente de completar)

1. **Chart.js se carga dos veces**: una vez globalmente desde
   `base/js.html` (cdnjs) y otra vez en `sales.html` (jsdelivr). No rompe
   nada (Chart.js tolera cargarse más de una vez), pero es una descarga y una
   inicialización de más en cada visita a `/analytics/sales`.
2. **El paquete de npm no se usa realmente**: `chart.js` quedó instalado en
   `node_modules/` pero el HTML sigue apuntando a CDNs externos, no al
   archivo que instaló `npm`. Para que la instalación tenga efecto, habría
   que importar `chart.js` desde `assets/js/app.js` (el pipeline de esbuild
   de este proyecto) en vez de (o además de) los `<script src>`.
3. **`get_sales_breakdown()` tiene dos llamadas a métodos que no existen**:
   - `recent.cart_data()` — no hay ningún método `cart_data` definido en
     `OrderManagerQuerySet`.
   - `shipped.totals_data()` — typo: el método que sí existe se llama
     `total_data()` (singular), no `totals_data()`.

   Si algo llegara a llamar `get_sales_breakdown()` hoy, fallaría con
   `AttributeError` en cualquiera de esas dos líneas.
4. **`by_week_data()` llama a `self.by_range(...)`**, un método que tampoco
   existe — probablemente debería ser `self.by_request(start_date, end_date)`
   (el método que sí se definió arriba, con ese nombre).
5. **`OrderManager.by_recent(self, request)` sigue llamando a
   `self.get_queryset().by_request(request)`**, pero `by_request` ahora
   espera `(start_date, end_date=None)` — pasarle un objeto `request` (de
   Django) en vez de una fecha rompería esta llamada también. Este método ya
   estaba marcado como pendiente desde la
   [clase 05](05-modelos-ordenes-django.md).
6. **La gráfica todavía no está conectada al backend**: `SalesView.get_context_data`
   (`src/analytics/views.py`) sigue calculando `recent_orders`,
   `shipped_orders` y `paid_orders` como listas de órdenes (para las tres
   columnas de texto), pero **no llama a `get_sales_breakdown()`** ni pasa
   ningún dato al `<script>` de Chart.js — de ahí que la gráfica use números
   fijos por ahora.
7. Sigue presente el `print(context)` de depuración señalado en la
   [clase 07](07-context-data-order-model.md).

## Próximos pasos sugeridos

- Corregir `cart_data` → método real (o quitar esa línea), `totals_data` →
  `total_data`, y `by_range` → `by_request` en `order/models.py`.
- Ajustar `OrderManager.by_recent` para que reciba fechas en vez de un
  `request`, o quitarlo si ya no se usa ese enfoque.
- En `SalesView.get_context_data`, llamar a `Order.objects.get_sales_breakdown()`
  y pasar `recent_data['total__sum']`, `shipped_data`, `paid_data`, etc. al
  contexto como JSON (`{{ chart_data|json_script:"chart-data" }}` es el
  patrón recomendado en Django) para que el `<script>` los lea en vez de
  tener `labels`/`data` hardcodeados.
- Quitar una de las dos cargas de Chart.js (dejar solo la global en
  `base/js.html`, o solo la local en `sales.html`, no ambas).
- Decidir si vale la pena integrar Chart.js al pipeline de esbuild
  (`assets/js/`) ahora que está en `package.json`, en vez de depender de un
  CDN externo.
