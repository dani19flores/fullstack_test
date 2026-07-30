# Clase: Modelos para gestionar órdenes

## Temas cubiertos en la clase

- Definir modelos para gestionar órdenes en un proyecto Django.
- Examinar el uso de señales `pre_save` y `post_save` en Django.
- Crear métodos en `OrderManager` para filtrar y ordenar órdenes.

## Contexto

Se agregó una nueva app, `order` (`src/order/`), pensada para representar el
pedido/orden de compra dentro del flujo de e-commerce (complementaria a la app
`ventas` de la [clase 04](04-vistas-ecommerce-ventas.md)):

```
src/order/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

Igual que en las clases anteriores, el archivo con contenido nuevo relevante
es [`models.py`](../../src/order/models.py); `admin.py`, `views.py` y
`tests.py` siguen en su estado por defecto de `startapp`.

## 1. El modelo `Order`

```python
class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True)
    order_id = models.CharField(max_length=120, blank=True)
    shipping_address = models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True)
    billing_address = models.ForeignKey(Address, related_name='billing_address', null=True, blank=True)
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    updated = models.BooleanField(auto_now=True)
    timestamp = models.BooleanField(auto_now_add=True)

    objects = OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def get_absolute_url(self):
        return reverse('orders:detail', kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == 'refunded':
            return 'Refunded order'
        elif self.status == 'shipped':
            return 'Shipped'
        return 'Shipping Soon'
```

Ideas clave del modelo:

- **`ORDER_STATUS_CHOICES`**: tupla de tuplas `(valor_interno, etiqueta)` que
  define el ciclo de vida de una orden (`created` → `paid` → `shipped` →
  `completed`, con `refunded`/`canceled` como salidas alternas). Se usa en
  `status` como `choices=`, lo que limita los valores válidos y hace que
  Django/el admin muestren la etiqueta legible en vez del valor crudo.
- **Relaciones (`ForeignKey`)**: la orden referencia un `BillingProfile`
  (perfil de facturación/usuario), dos `Address` distintas (envío y
  facturación — de ahí el `related_name` en cada una, para poder acceder
  como `address.shipping_address` y `address.billing_address` desde el otro
  lado de la relación) y un `Cart` (el carrito que originó la orden).
- **`shipping_total`**: costo de envío con un valor por defecto (`5.99`).
- **`get_status()`**: traduce el valor interno de `status` a un mensaje más
  amigable para mostrar en pantalla, sin modificar el dato guardado en base
  de datos.
- **`get_absolute_url()`**: patrón estándar de Django para poder hacer
  `{{ order.get_absolute_url }}` en un template y obtener el link al detalle
  de esa orden, en vez de armar la URL a mano.
- **`Meta.ordering`**: por defecto, cualquier consulta a `Order.objects.all()`
  devuelve primero las órdenes más recientes (por `timestamp` y `updated`
  descendente).

## 2. Señales `pre_save` y `post_save`

El archivo importa ambas señales:

```python
from django.db.models.signals import post_save, pre_save
```

Estas señales son el mecanismo de Django para ejecutar código automáticamente
quat un modelo se guarda, sin tener que sobreescribir `save()`:

- **`pre_save`**: se dispara *antes* de que el registro se escriba en la base
  de datos. Es el lugar típico para calcular o transformar un campo antes de
  guardarlo — por ejemplo, generar el `order_id` único de esta orden (de ahí
  el import ya presente de `unique_order_id_generator` desde
  `eccomerce.utils`, pensado para usarse en un receptor de `pre_save`).
- **`post_save`**: se dispara *después* de guardar el registro. Se usa
  típicamente para acciones que dependen de que el objeto ya tenga un `id`
  asignado (por ejemplo, crear un objeto relacionado la primera vez que se
  crea la orden, `created=True`).

El patrón general para "escuchar" una señal en Django es:

```python
def alguna_funcion(sender, instance, *args, **kwargs):
    ...

pre_save.connect(alguna_funcion, sender=Order)
```

o usando el decorador `@receiver(pre_save, sender=Order)`.

**Importante**: en el estado actual de `models.py`, las señales están
**importadas pero no conectadas todavía** — no hay ninguna función receptora
ni ninguna llamada a `.connect()`. Es decir, esta clase examina el concepto y
deja preparado el terreno (los imports, y el import de
`unique_order_id_generator` que se usaría dentro del receptor de
`pre_save`), pero la conexión real de la señal queda pendiente para una
próxima clase.

## 3. Métodos de `OrderManager` para filtrar y ordenar

```python
class OrderManagerQuerySet(models.query.QuerySet):
    def recent(self):
        return self.order_by('-updated', '-timestamp')

    def by_status(self, status='shipped'):
        return self.filter(status=status)

    def not_refunded(self):
        return self.exclude(status='refunded')

    def not_created(self):
        return self.exclude(status='created')

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_recent(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        created = False
        qs = self.get_queryset().filter(
            billing_profile__user=billing_profile,
            cart=cart_obj,
            active=True,
            status='created'
        )
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(
                billing_profile__user=billing_profile,
                cart=cart_obj
            )
            created = True
        return obj, created
```

- **`OrderManagerQuerySet`**: un `QuerySet` personalizado con métodos de
  filtrado/orden encadenables (`Order.objects.not_refunded().by_status('paid')`,
  por ejemplo):
  - `recent()`: ordena por más recientemente actualizado/creado.
  - `by_status(status)`: filtra por un estado puntual del ciclo de vida.
  - `not_refunded()` / `not_created()`: excluyen órdenes reembolsadas, o
    excluyen las que todavía están en estado "created" (es decir, que ni
    siquiera se pagaron todavía).
- **`OrderManager`**: el manager del modelo (`Order.objects`), que en vez de
  devolver un `QuerySet` normal devuelve el `OrderManagerQuerySet` de arriba
  (así los métodos custom quedan disponibles directamente en
  `Order.objects...`).
  - **`new_or_get(billing_profile, cart_obj)`**: patrón "buscar o crear" —
    si ya existe una orden activa en estado `created` para ese perfil de
    facturación y carrito, la reutiliza; si no, crea una nueva. Devuelve una
    tupla `(orden, created)`, igual que `get_or_create()` de Django.

## Estado actual del código (pendiente de completar)

Este modelo depende de piezas que **todavía no existen en este proyecto**, así
que por ahora `order` se dejó **fuera de `INSTALLED_APPS`** a propósito: si se
registrara, el proyecto completo no arrancaría.

1. **Imports de apps inexistentes**: `address.models.Address`,
   `billing.models.BillingProfile`, `carts.models.Cart`,
   `eccomerce.utils.unique_order_id_generator` y `products.models.products`
   no existen en `fullstack_test` — son apps de un proyecto de referencia más
   grande (el curso de e-commerce completo). Este proyecto, hasta ahora, solo
   tiene `ventas.Product` (clase 04), no `carts`, `billing` ni `address`.
2. **Import roto**: `from django.core.urlresolvers import reverse` — ese
   módulo ya no existe en Django 6 (mismo tipo de error que se corrigió en
   `accounts/models.py` en la [clase 03](03-desarrolla-template-ventas.md),
   aunque aquí el nombre del módulo está bien escrito, solo desactualizado;
   debería ser `django.urls`).
3. **`ForeignKey` sin `on_delete`**: `billing_profile`, `shipping_address`,
   `billing_address` y `cart` no especifican `on_delete`, obligatorio desde
   Django 2.0. Sin esto, Django ni siquiera puede cargar la clase del modelo.
4. **Tipo de campo incorrecto**: `updated` y `timestamp` están declarados como
   `models.BooleanField(auto_now=True)` / `models.BooleanField(auto_now_add=True)`.
   `auto_now`/`auto_now_add` son argumentos de `DateField`/`DateTimeField`, no
   de `BooleanField` — deberían ser `models.DateTimeField(...)`.
5. **Bug en `__str__`**: `return super().order_id` no tiene sentido — `super()`
   no expone los campos de la instancia. Debería ser `return self.order_id`.
6. **`OrderManager.by_recent` llama a un método que no existe**:
   `self.get_queryset().by_request(request)`, pero `OrderManagerQuerySet` solo
   define `recent()`, `by_status()`, `not_refunded()` y `not_created()` — no
   `by_request()`. Probablemente debería llamar a `.recent()`.
7. **`new_or_get` mezcla una ruta de lookup (`billing_profile__user=...`) con
   una creación de objeto**: `billing_profile__user=billing_profile` es válido
   en `.filter()` (siempre que `BillingProfile` tenga un campo `user`), pero
   se reutiliza igual dentro de `self.model.objects.create(...)`, donde
   `billing_profile__user` no es un campo real del modelo `Order` — eso
   fallaría en tiempo de ejecución. Debería ser `billing_profile=billing_profile`
   en ambos lugares (o `billing_profile__user=billing_profile.user` si la
   intención era comparar contra el usuario asociado).
8. **Señales sin conectar**: como se explicó arriba, `pre_save`/`post_save`
   están importadas pero no hay ningún receptor registrado todavía.
9. **Sin migraciones** y **sin registrar en `INSTALLED_APPS`**.

## Próximos pasos sugeridos

- Decidir si este proyecto va a construir sus propias apps `carts`,
  `billing` y `address` (siguiendo el curso de referencia), o si conviene
  adaptar `Order` para que dependa de lo que ya existe (`ventas.Product`) en
  vez de esas apps.
- Corregir el import de `reverse`, agregar `on_delete` a las `ForeignKey`, y
  cambiar `updated`/`timestamp` a `DateTimeField`.
- Corregir `__str__` y `OrderManager.by_recent`.
- Conectar un receptor de `pre_save` que genere `order_id` con
  `unique_order_id_generator` antes de guardar.
- Registrar `order` en `INSTALLED_APPS` y generar sus migraciones, una vez
  resueltas sus dependencias.
