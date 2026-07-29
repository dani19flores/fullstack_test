# Clase: Desarrolla el template de ventas

## Temas cubiertos en la clase

- Organizar los archivos de templates en carpetas específicas por aplicación.
- Configurar las URLs para que reflejen la estructura de la aplicación Analytics.
- Validar la correcta visualización del template de ventas con diferentes estados de autenticación.

## Contexto

Esta clase termina de conectar la vista `SalesView` (creada en la
[clase 02](02-extiende-clases-base-vistas.md)) con Django: se registran las
apps, se le da una URL real, se organiza su template, y se corrigen varios
errores que impedían que la página cargara. Archivos tocados:

```
modificado:  src/accounts/models.py
modificado:  src/config/settings.py
modificado:  src/config/urls.py
modificado:  src/templates/layouts/base.html
nuevo:       .gitattributes
nuevo:       src/analytics/urls.py
nuevo:       src/templates/analytics/sales.html
nuevo:       src/templates/base/css.html
nuevo:       src/templates/base/js.html
nuevo:       src/templates/base/navbar.html
```

## 1. Organizar los templates en carpetas por aplicación

Django resuelve `template_name = 'analytics/sales.html'` buscando ese *path*
relativo dentro de cada carpeta configurada en `TEMPLATES`. En este proyecto
hay dos formas válidas de ubicar ese archivo, y ambas funcionan porque
`src/config/settings.py` incluye `src/templates/` en `DIRS`:

- **Namespacing por app** (convención recomendada por Django): guardar el
  archivo en `src/analytics/templates/analytics/sales.html`. La subcarpeta
  `analytics/` dentro de `templates/` evita que choque con un `sales.html` de
  otra app.
- **Carpeta global del proyecto** (la que se usó al final en esta clase):
  `src/templates/analytics/sales.html`. Como
  `TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]`, el
  `filesystem.Loader` encuentra `analytics/sales.html` ahí igual, sin
  necesidad de que la app tenga su propia carpeta `templates/`.

Se optó por la segunda opción, dejando todos los templates de "features"
(no solo los de layout) centralizados bajo `src/templates/`, agrupados por
subcarpeta según la app a la que pertenecen (`src/templates/analytics/...`).

También se completó `src/templates/layouts/base.html`, el layout base creado
en la clase anterior, agregando las plantillas parciales que le faltaban:

- `src/templates/base/css.html`
- `src/templates/base/js.html`
- `src/templates/base/navbar.html`

Sin ellas, cualquier `{% include %}` en `base.html` lanzaba
`TemplateDoesNotExist`. Además se corrigieron tres errores de HTML que ya
había en `base.html`: la clase `alert-sucess` (typo) → `alert-success`, un
`<br` sin cerrar → `<br>`, y faltaba la etiqueta de cierre `</html>`.

`src/templates/analytics/sales.html` extiende ese layout:

```html
{% extends 'layouts/base.html' %}

{% block content %}
    <div class="row">
        <div class="col-12">
            <h1>Sales Analytics</h1>
        </div>
    </div>
{% endblock %}
```

Solo sobreescribe el bloque `content`; el resto del HTML (head, navbar, CSS,
JS, mensajes) lo hereda del layout.

## 2. Configurar las URLs de Analytics

Se creó [`src/analytics/urls.py`](../../src/analytics/urls.py):

```python
from django.urls import path
from analytics import views

urlpatterns = [
    path("sales", views.SalesView.as_view(), name="sales-analytics"),
]
```

Y se conectó ese URLconf en
[`src/config/urls.py`](../../src/config/urls.py) con un prefijo `analytics/`:

```python
urlpatterns = [
    path("up/", include("up.urls")),
    path("", include("pages.urls")),
    path("analytics/", include("analytics.urls")),
    path("admin/", admin.site.urls),
    path("__debug__/", include("debug_toolbar.urls")),
]
```

Esto refleja la estructura de la app: cada app tiene su propio `urls.py` con
sus rutas relativas, y `config/urls.py` solo las monta bajo un prefijo
(`analytics/` → toda ruta de esa app cuelga de ahí). Con `path("sales", ...)`
dentro de `analytics/urls.py`, la URL final queda en `/analytics/sales`.

Para que Django reconociera esta app (y por lo tanto sus templates, modelos y
migraciones), también se agregó a `INSTALLED_APPS` en
[`src/config/settings.py`](../../src/config/settings.py), junto con
`accounts` (pendiente desde la clase 1):

```python
INSTALLED_APPS = [
    "pages.apps.PagesConfig",
    "accounts.apps.AccountsConfig",
    "analytics.apps.AnalyticsConfig",
    "django.contrib.admin",
    ...
]
```

Al registrar `accounts`, Django cargó `accounts/models.py` por primera vez, lo
cual expuso un import roto que venía arrastrándose desde la clase 1:
`from django.core.urlsrolvers import reverse` (typo, y ese módulo no existe
desde hace varias versiones de Django). Como `reverse` no se usaba en ningún
lado del archivo, se eliminó el import en vez de corregirlo.

## 3. Validar el template con distintos estados de autenticación

`SalesView` combina dos mecanismos de protección
([`src/analytics/views.py`](../../src/analytics/views.py)):

```python
class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        return super(SalesView, self).dispatch(*args, **kwargs)
```

Se probaron los tres estados posibles de autenticación contra
`http://localhost:8000/analytics/sales`:

| Estado del usuario                        | Resultado obtenido |
|--------------------------------------------|---------------------|
| Anónimo (sin sesión)                       | `401 Unauthorized` (texto plano, `dispatch` corta antes de llegar a `LoginRequiredMixin`) |
| Autenticado, `is_staff=False`               | `401 Unauthorized` |
| Autenticado, `is_staff=True`                | `200 OK`, renderiza `analytics/sales.html` dentro del layout |

Es decir: como el chequeo manual `if not user.is_staff` se ejecuta **antes**
de llamar a `super().dispatch()`, `AnonymousUser.is_staff` (que siempre es
`False`) hace que cualquier visitante no autenticado reciba directamente
"Unauthorized" — el `LoginRequiredMixin` nunca llega a redirigir al login.
Este es el comportamiento esperado para este ejercicio (no un bug a corregir):
la app no distingue "no logueado" de "logueado pero sin permisos", ambos
casos devuelven la misma respuesta 401.

Para probar el caso "autenticado y staff" se creó un superusuario de prueba
con `createsuperuser` (usuario `dani_admin`), y se confirmó por separado (vía
el motor de templates en `manage.py shell`) que `analytics/sales.html` se
resuelve y renderiza correctamente.

## Estado actual del código (pendiente de completar)

1. **No hay vista de login propia**: Django redirige por defecto a
   `/accounts/login/` cuando un mixin de autenticación lo requiere, pero esa
   URL no existe todavía (`accounts` no tiene `urls.py` ni vista de login) —
   da 404. Como `SalesView` responde 401 antes de que el mixin intente
   redirigir, esto no bloquea la clase actual, pero sí será necesario en
   cuanto se quiera un flujo real de login.
2. **`AUTH_USER_MODEL` sigue sin configurarse**: la app sigue autenticando con
   `django.contrib.auth.models.User` (el modelo por defecto), no con
   `accounts.User`. Ambos exponen `is_staff`, así que `SalesView` funciona de
   cualquier forma, pero el modelo de usuario personalizado de la clase 1
   todavía no está activo.
3. **`get_context_data` no agrega nada nuevo** en `SalesView` — sigue como
   marcador de posición para cuando se agreguen datos reales de ventas al
   contexto.
4. Sin migraciones para `accounts` ni `analytics` todavía.

## Próximos pasos sugeridos

- Crear la vista y el template de login en `accounts` para completar el flujo
  de autenticación.
- Definir `AUTH_USER_MODEL = "accounts.User"` y generar las migraciones
  correspondientes.
- Agregar datos reales de ventas en `SalesView.get_context_data`.
