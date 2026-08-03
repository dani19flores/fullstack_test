# Clase: Construye los modelos de Billing Profile, Cart y Product

## Temas cubiertos en la clase

- Crear el modelo de Billing Profile con relaciones y atributos adecuados.
- Diseñar el modelo de Carrito (Cart) con relaciones many-to-many y campos
  esenciales.
- Desarrollar el modelo de Producto (Product) con campos para título,
  descripción, precio y atributos adicionales.

## Contexto

Continuando con las apps creadas en la [clase 05](05-modelos-ordenes-django.md)
(`addresses`, `billing`, `carts`, `products`, `eccomerce`, pensadas para que
`order.Order` tenga todas sus dependencias), esta clase llena el contenido de
tres de esos modelos:

```
src/billing/models.py
src/carts/models.py
src/products/models.py
```

También se completó, como pieza de apoyo, `GuestEmail` en
[`src/accounts/models.py`](../../src/accounts/models.py) (checkout de
invitados sin cuenta), porque `billing.BillingProfile` lo necesita.

## 1. `BillingProfile` (`src/billing/models.py`)

```python
User = settings.AUTH_USER_MODEL

class BillingProfile(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    customer_id = models.CharField(max_length=120, null=True, blank=True)
```

- **`user` como `OneToOneField`**: cada usuario tiene **como máximo un**
  perfil de facturación (a diferencia de un `ForeignKey`, que permitiría
  varios). Es `null=True, blank=True` a propósito: permite crear un
  `BillingProfile` para un comprador invitado (sin cuenta), asociado solo por
  `email`, y no por `user`.
- **`User = settings.AUTH_USER_MODEL`**: en vez de importar el modelo de
  usuario directamente, se referencia mediante el *setting* de Django. Es la
  forma recomendada de apuntar al modelo de usuario activo (sea el de
  `django.contrib.auth` o uno personalizado como `accounts.User`) sin crear
  una dependencia circular de imports.
- **`email`**: independiente del `user`, para poder tener un perfil de
  facturación aunque no haya cuenta (checkout de invitado vía `GuestEmail`).
- **`customer_id`**: campo pensado para guardar el ID de cliente de un
  proveedor de pagos externo (ej. Stripe), típico en este tipo de modelos.
- **`active`, `update`, `timestamp`**: campos de auditoría/estado estándar,
  igual que en otros modelos del proyecto.

Sobre el import `from accounts.models import GuestEmail`, se agregó ese
modelo de apoyo:

```python
class GuestEmail(models.Model):
    email = models.EmailField()
    active = models.BooleanField(default=True)
    update = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
```

Solo guarda el email de un comprador que todavía no tiene cuenta — el primer
paso de un flujo de "checkout como invitado".

## 2. `Product` (`src/products/models.py`)

```python
def upload_image_path(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(blank=True, unique=True)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=20, default=39.99)
    image = models.ImageField(upload_to=upload_image_path, blank=True, null=True)
    feactured = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_digital = models.BooleanField(default=False)

    def __str__(self):
        return self.title
```

Campos, tal como pedía el enunciado ("título, descripción, precio y atributos
adicionales"):

- **`title` / `description` / `price`**: lo básico de cualquier producto.
- **`slug`**: versión URL-friendly del título (`unique=True`, para usarla en
  rutas tipo `/products/mi-producto/`); queda `blank=True` porque, como se ve
  más abajo, la idea es generarlo automáticamente (con una señal `pre_save`,
  el mismo mecanismo que se introdujo conceptualmente en la
  [clase 05](05-modelos-ordenes-django.md)), no escribirlo a mano.
- **`image`**: usa `upload_to=upload_image_path`, una función propia en vez
  de una ruta fija, para poder decidir dinámicamente el nombre/carpeta de
  cada imagen subida.
- **`feactured`** *(sic)*: booleano para marcar productos destacados.
- **`active`**: para poder "despublicar" un producto sin borrarlo.
- **`is_digital`**: distingue productos digitales de físicos — es el campo
  que usa `Cart.is_digital` (ver más abajo) para saber si todo el carrito es
  descargable (por ejemplo, para saltarse el paso de dirección de envío).

## 3. `Cart` (`src/carts/models.py`)

```python
User = settings.AUTH_USER_MODEL

class Cart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @property
    def is_digital(self):
        qs = self.products.all()
        new_qa = qs.filter(is_digital=False)
        if new_qa.exists():
            return False
        return True
```

- **`user` como `ForeignKey`** (no `OneToOneField`, a diferencia de
  `BillingProfile`): un usuario puede tener varios carritos a lo largo del
  tiempo (uno activo, otros ya convertidos en orden). También es
  `null=True, blank=True` para soportar carritos de visitantes anónimos.
- **`products` como `ManyToManyField(Product, blank=True)`**: es la relación
  many-to-many que pedía el enunciado — un carrito tiene muchos productos, y
  un mismo producto puede estar en muchos carritos distintos. `blank=True`
  permite que el carrito exista vacío (recién creado, antes de agregar nada).
- **`subtotal` / `total`**: se guardan como campos propios (no se calculan al
  vuelo cada vez) — pensados para recalcularse vía una señal cada vez que
  cambian los productos del carrito (otro caso de uso típico de
  `pre_save`/`post_save`, ya importadas en este archivo aunque, igual que en
  `order` y `products`, todavía sin conectar).
- **`is_digital`** (`@property`): no es un campo de base de datos, sino una
  propiedad calculada — revisa todos los productos del carrito y, si
  encuentra al menos uno que **no** sea digital (`is_digital=False`),
  devuelve `False`. Solo devuelve `True` cuando *todos* los productos del
  carrito son digitales.

## Estado actual del código (pendiente de completar)

1. **`upload_image_path` no sigue la firma que espera Django**: `upload_to`
   debe ser una función `(instance, filename) -> str` que devuelva la ruta
   final donde guardar el archivo. Tal como está escrita
   (`upload_image_path(filepath)`, que hace `os.path.basename(filepath)`),
   Django la va a llamar con `(instance, filename)` y fallaría, porque
   `os.path.basename()` esperaría una cadena de texto, no una instancia de
   `Product`.
2. **Typo `feactured`** (debería ser `featured`) — no rompe nada, pero
   quedaría como el nombre del campo en la base de datos y en el admin si no
   se corrige antes de migrar.
3. **`slug` no se genera automáticamente todavía**: queda `blank=True` sin
   ningún valor por defecto ni señal `pre_save` conectada que lo derive de
   `title` — hoy tocaría llenarlo a mano.
4. **Señales importadas y sin conectar** en los tres archivos
   (`pre_save`, `post_save`): siguen preparadas para usarse (recalcular
   `Cart.subtotal`/`total` al modificar `products`, generar el `slug` de
   `Product`, etc.) pero sin ningún receptor todavía — mismo patrón señalado
   en la clase anterior para `order`.
5. **Ninguna de las apps nuevas está en `INSTALLED_APPS`** todavía
   (`accounts` tampoco lo está para efectos de `GuestEmail`... en realidad sí
   está, pero falta `billing`, `carts`, `products`, `addresses`, `order`), y
   no hay migraciones generadas para ninguna.
6. Imports sin usar en varios archivos (`Decimal`, `settings` en algunos
   casos) que quedaron de plantilla.

## Próximos pasos sugeridos

- Corregir `upload_image_path` para que reciba `(instance, filename)`.
- Conectar señales `pre_save` en `Product` (generar `slug`) y en `Cart`
  (recalcular `subtotal`/`total` cuando cambian `products`), retomando lo
  visto conceptualmente en la clase 05.
- Registrar `addresses`, `billing`, `carts`, `products` y `order` en
  `INSTALLED_APPS`, en ese orden de dependencia, y generar sus migraciones.
