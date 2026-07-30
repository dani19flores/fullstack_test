# Actividad: Configurar las vistas para el e-commerce (app `ventas`)

## Enunciado de la actividad

Configurar las vistas para el e-commerce aplicando los pasos vistos en este
módulo:

1. Importar el repositorio de referencia (clonar
   [nickjj/docker-django-example](https://github.com/nickjj/docker-django-example))
   y abrirlo en VS Code.
2. Configurar los métodos y vistas (`views.py`) de la app de ventas.
3. Crear el template de ventas (`templates/ventas/ventas.html`).
4. Configurar las URLs (`urls.py`) de la app de ventas.
5. Probar y depurar en el navegador.
6. Subir el código a GitHub con el nombre "Vistas del e-commerce".
7. Entregar un PDF con el link al repositorio y el código.

El paso 1 (clonar el repositorio de referencia) ya estaba resuelto: este
mismo proyecto (`fullstack_test`) parte de esa plantilla
([docker-django-example](https://github.com/nickjj/docker-django-example)),
así que la actividad se hizo directamente sobre él en vez de clonar una copia
nueva.

## Decisiones tomadas antes de programar

No existía ningún modelo de producto ni app de e-commerce en el proyecto
todavía, así que se definió el alcance antes de escribir código:

| Decisión | Elegido |
|---|---|
| Nombre de la app | `ventas` (coincide literalmente con el enunciado) |
| Origen de los productos | Modelo `Product` real, con migración y datos de prueba (no hardcodeado) |
| Carrito de compras | En `request.session` (sin login ni tabla en base de datos) |

## 1. Modelo y vistas (`src/ventas/models.py`, `src/ventas/views.py`)

Se creó la app `ventas` con un modelo simple:

```python
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
```

Y tres vistas basadas en función (siguiendo el enunciado: "utiliza `render`,
`HttpResponse`, `redirect`, etc."), una por cada operación que pedía la
actividad:

- **`product_list`**: lista todos los `Product`, y arma el resumen del
  carrito leyendo `request.session['cart']` (un diccionario
  `{id_producto: cantidad}`). Renderiza `ventas/ventas.html` con
  `products`, `cart_items` y `cart_total` en el contexto.
- **`add_to_cart`**: agrega (o incrementa) un producto en el carrito de la
  sesión y redirige de vuelta a la lista con un mensaje de éxito
  (`django.contrib.messages`).
- **`process_order`**: si el carrito tiene productos, lo vacía y muestra un
  mensaje de confirmación; si está vacío, muestra un mensaje de error.

`add_to_cart` y `process_order` están decoradas con `@require_POST` — son
operaciones que cambian estado (agregan al carrito, vacían el carrito), así
que no deben ser accesibles por `GET` (evita, por ejemplo, que un link o un
crawler dispare la acción por accidente).

## 2. Template (`src/ventas/templates/ventas/ventas.html`)

Se respetó al pie de la letra la estructura de carpetas que pedía el
enunciado: `templates/` dentro de la app, subcarpeta `ventas/`, archivo
`ventas.html`. A diferencia del template de `analytics` (que se movió a la
carpeta global `src/templates/`), este quedó dentro de la propia app, como
ejemplo de la otra convención válida de Django (namespacing por app).

El template extiende `layouts/base.html` (el layout creado en la
[clase 02](02-extiende-clases-base-vistas.md)) y sobrescribe `content` con
tres secciones dinámicas, usando el lenguaje de plantillas de Django:

- **Lista de productos** (`{% for product in products %}`), cada uno con su
  propio formulario `POST` hacia `ventas:add-to-cart`.
- **Carrito de compras** (`{% for item in cart_items %}` + `cart_total`).
- **Formulario de pedido**: un solo botón "Procesar pedido" que hace `POST`
  a `ventas:process-order`, visible solo si el carrito tiene productos.

## 3. URLs (`src/ventas/urls.py`)

```python
app_name = 'ventas'

urlpatterns = [
    path('', views.product_list, name='product-list'),
    path('agregar/<int:product_id>/', views.add_to_cart, name='add-to-cart'),
    path('pedido/', views.process_order, name='process-order'),
]
```

Se usó un `app_name` (namespace) para poder referenciar las URLs desde el
template como `{% url 'ventas:add-to-cart' product.id %}` sin colisionar con
nombres de otras apps. Se montó en
[`src/config/urls.py`](../../src/config/urls.py) bajo el prefijo `ventas/`,
y se registró `ventas.apps.VentasConfig` en `INSTALLED_APPS`
([`src/config/settings.py`](../../src/config/settings.py)).

## 4. Prueba y depuración

Se generó la migración (`makemigrations ventas` / `migrate ventas`), se
cargaron 3 productos de prueba (Camiseta, Taza, Gorra) y se probó el flujo
completo por HTTP (con cookies de sesión y token CSRF) contra
`http://localhost:8000/ventas/`:

| Paso | Resultado |
|---|---|
| `GET /ventas/` | `200`, muestra los 3 productos y carrito vacío |
| `POST /ventas/agregar/<id>/` | `302` (redirect a la lista) |
| `GET /ventas/` (después de agregar) | `200`, carrito muestra el producto y el total correcto (`$19.99`) |
| `POST /ventas/pedido/` | `302` (redirect a la lista) |
| `GET /ventas/` (después de procesar) | `200`, mensaje "Tu pedido fue procesado correctamente." y carrito vacío de nuevo |

Sin errores en los logs del contenedor `web` durante toda la prueba.

## Estado actual del código (pendiente de completar)

1. **El carrito no valida cantidades ni stock**: `add_to_cart` siempre suma 1,
   sin límite ni verificación de inventario (no hay campo de stock en
   `Product` todavía).
2. **`process_order` no crea ningún registro persistente** (no hay modelo
   `Order`/`OrderItem`): "procesar el pedido" hoy solo vacía la sesión y
   muestra un mensaje, no queda ningún historial de compras en la base de
   datos.
3. **Sin control de acceso**: cualquier visitante (autenticado o no) puede
   comprar; no se integró con el modelo de usuario de `accounts` ni con las
   protecciones vistas en `analytics.SalesView`.
4. **Los productos de prueba se cargaron a mano por `shell`**, no hay un
   fixture ni una migración de datos para reproducirlos en otro entorno.

## Próximos pasos sugeridos

- Agregar un modelo `Order`/`OrderItem` para persistir los pedidos.
- Agregar cantidad/stock al `Product` y validar en `add_to_cart`.
- Decidir si el carrito debe requerir login (ligarlo a `accounts.User`) en vez
  de sesión anónima.
- Agregar un fixture de productos de ejemplo (`loaddata`) para no depender de
  cargarlos manualmente.
