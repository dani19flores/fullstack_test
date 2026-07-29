# Clase: Extiende las clases base para codificar las vistas

## Temas cubiertos en la clase

- Describir la personalización de métodos en modelos de usuario en Django.
- Implementar vistas protegidas utilizando mixins de autenticación.
- Evaluar la estructura y funcionalidad de plantillas base en Django.

## Contexto

Cambios en *staged* (`git status`) para esta clase:

```
modificado:  src/accounts/models.py
nuevo:       src/analytics/__init__.py
nuevo:       src/analytics/admin.py
nuevo:       src/analytics/apps.py
nuevo:       src/analytics/migrations/__init__.py
nuevo:       src/analytics/models.py
nuevo:       src/analytics/tests.py
nuevo:       src/analytics/views.py
nuevo:       src/templates/layouts/base.html
```

Se completan métodos que faltaban en el modelo de usuario (clase anterior,
[01-modelos-usuario-django-orm.md](01-modelos-usuario-django-orm.md)), se crea
una nueva app `analytics` con una vista protegida, y se agrega la primera
plantilla base del proyecto.

## 1. Personalización de métodos en el modelo de usuario

Sobre [`src/accounts/models.py`](../../src/accounts/models.py), se agregaron al
final de la clase `User` los métodos que Django espera encontrar en cualquier
modelo que reemplace al `User` por defecto (heredar de `AbstractBaseUser` no los
trae incluidos, hay que escribirlos a mano):

```python
def __str__(self):
    return self.email

def get_full_name(self):
    if self.full_name:
        return self.full_name
    return self.email

def get_short_name(self):
    return self.email

def has_perm(self, perm, obj=None):
    return True

def has_module_perms(self, app_label):
    return True

@property
def is_staff(self):
    if self.is_admin:
        return True
    return self.staff

@property
def is_admin(self):
    return self.admin
```

- **`__str__`**: cómo se muestra el usuario en el admin de Django y en `repr()`
  (usa el email, ya que no hay `username`).
- **`get_full_name` / `get_short_name`**: métodos que Django (y cosas como el
  saludo en el admin) esperan encontrar en cualquier modelo de usuario;
  `get_full_name` cae de vuelta al email si `full_name` está vacío.
- **`has_perm` / `has_module_perms`**: aquí están simplificados devolviendo
  siempre `True` (es decir, cualquier usuario autenticado tiene todos los
  permisos). Es la versión "de curso" para no depender todavía del sistema de
  permisos de Django; en un proyecto real normalmente se delega a
  `PermissionsMixin` o se filtra por `is_admin`.
- **`is_staff`** e **`is_admin`** como `@property`: traducen los campos "planos"
  del modelo (`staff`, `admin`) a las propiedades que Django y el admin site
  consultan internamente (`user.is_staff`, y en `SalesView` más abajo,
  `user.is_staff`). Un admin (`is_admin=True`) automáticamente también cuenta
  como staff.

Con esto, el modelo `User` ya cumple la interfaz mínima que pide
`django.contrib.auth` para autenticar y para usarse en el panel de
administración.

## 2. Vistas protegidas con mixins de autenticación (app `analytics`)

Se creó la app `analytics` (`django-admin startapp analytics`) con una vista de
ejemplo en [`src/analytics/views.py`](../../src/analytics/views.py):

```python
class SalesView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/sales.html'

    def dispatch(self, *args, **kwargs):
        user = self.request.user
        if not user.is_staff:
            return HttpResponse('Unauthorized', status=401)
        return super(SalesView, self).dispatch(*args, **kwargs)

    def get_context_data(self,  *args, **kwargs):
         return super(SalesView, self).get_context_data(*args, **kwargs)
```

Ideas clave de vistas basadas en clases (CBV) que cubre este ejemplo:

- **`TemplateView`**: vista genérica de Django que solo renderiza una plantilla
  (`template_name`), sin lógica de formularios ni de modelos.
- **`LoginRequiredMixin`**: mixin de `django.contrib.auth.mixins` que se
  antepone a `TemplateView` en la herencia. Si el usuario no está autenticado,
  redirige automáticamente al login (`LOGIN_URL`) antes de que se ejecute
  cualquier otro código de la vista. El **orden de la herencia importa**: los
  mixins van primero, la vista genérica al final
  (`class SalesView(LoginRequiredMixin, TemplateView)`).
- **`dispatch()`**: es el método que Django llama primero en cualquier CBV
  (decide qué método usar según el verbo HTTP: `get`, `post`, etc.). Aquí se
  sobreescribe para agregar una segunda capa de protección **además** del
  mixin: si el usuario sí está logueado pero no es `is_staff`, la vista
  responde `401 Unauthorized` en vez de renderizar. Es decir:
  - No autenticado → lo resuelve `LoginRequiredMixin` (redirect a login).
  - Autenticado pero no staff → lo resuelve el `dispatch()` manual (401).
  - Autenticado y staff → sigue el flujo normal (`super().dispatch(...)`).
- **`get_context_data()`**: sobreescrito pero, tal como está ahorita, no agrega
  nada nuevo al contexto (solo llama a `super()`); queda ahí como el punto
  donde en una próxima clase se agregarían los datos de ventas para la
  plantilla `analytics/sales.html`.

El resto de los archivos de la app (`models.py`, `admin.py`, `tests.py`) siguen
en su estado por defecto de `startapp`, sin contenido propio todavía.

## 3. Estructura de la plantilla base (`layouts/base.html`)

Se agregó la primera plantilla base del proyecto en
[`src/templates/layouts/base.html`](../../src/templates/layouts/base.html),
pensada para que el resto de las plantillas hereden de ella con
`{% extends "layouts/base.html" %}`.

Piezas de la plantilla:

- **`{% load static %}`**: habilita la etiqueta `{% static %}` en el resto del
  archivo (por ahora no se usa directamente aquí, pero la dejan cargada para
  los `include`).
- **`{% include 'base/css.html' %}` / `{% include 'base/js.html' %}`**: separan
  los `<link>` de CSS y los `<script>` de JS en archivos aparte, para no
  ensuciar la plantilla base y poder reutilizarlos.
- **`{% include 'base/navbar.html' with brand_name="eCommerce" %}`**: incluye
  una barra de navegación reutilizable, pasándole una variable (`brand_name`)
  desde la plantilla que la incluye — así el mismo navbar sirve para distintos
  proyectos/nombres sin duplicar código.
- **Bloque de mensajes (`{% if messages %}`)**: usa el *messages framework* de
  Django (`django.contrib.messages`) para mostrar notificaciones (errores,
  confirmaciones, etc.) que las vistas dejan con `messages.add_message(...)`.
- **`{% block base_head %}`, `{% block content %}`, `{% block javascript %}`**:
  los tres puntos de extensión de la plantilla. Cualquier plantilla hija puede
  sobreescribir uno o varios de estos bloques sin tocar el resto del layout
  (patrón estándar de herencia de plantillas en Django).

## Estado actual del código (pendiente de completar)

1. **Plantillas incluidas que todavía no existen**: `base.html` hace
   `{% include %}` de `base/css.html`, `base/navbar.html` y `base/js.html`,
   pero esos archivos no están creados todavía en `src/templates/base/`. Hasta
   que se agreguen, cualquier vista que use este layout va a lanzar
   `TemplateDoesNotExist`.
2. **HTML incompleto/con errores** en `base.html`:
   - Falta la etiqueta de cierre `</html>` (el archivo termina en `</body>`).
   - `<span ...>{{ message }} <br` — el `<br` no está cerrado (falta `>` o
     usar `<br>` / `<br />` sin más contenido dentro del `<span>`).
   - Clase CSS `alert-sucess` con typo (debería ser `alert-success`).
3. **`analytics` no está registrado** en `INSTALLED_APPS`
   ([`src/config/settings.py`](../../src/config/settings.py)), así que Django
   todavía no reconoce esta app ni sus templates.
4. **Sin URLs todavía**: no existe `src/analytics/urls.py` ni una entrada en
   [`src/config/urls.py`](../../src/config/urls.py) que apunte a `SalesView`,
   por lo que la vista no es alcanzable desde el navegador aún.
5. **`accounts` sigue sin estar registrado** ni tiene `AUTH_USER_MODEL`
   configurado (pendiente ya señalado en la clase anterior); esto también
   bloquea que `analytics.SalesView` funcione en la práctica, porque
   `LoginRequiredMixin` y `user.is_staff` dependen de que el modelo de usuario
   personalizado esté activo.
6. **`has_perm` / `has_module_perms` siempre devuelven `True`**: es una
   simplificación válida para esta etapa del curso, pero no está pensada para
   producción (todo usuario autenticado tendría todos los permisos).

## Próximos pasos sugeridos

- Registrar `accounts` y `analytics` en `INSTALLED_APPS`, y definir
  `AUTH_USER_MODEL = "accounts.User"`.
- Crear las plantillas parciales `base/css.html`, `base/navbar.html` y
  `base/js.html`, y corregir el HTML de `base.html`.
- Crear `analytics/urls.py` y conectarlo en `config/urls.py` para poder probar
  `SalesView` en el navegador.
- Crear la plantilla `analytics/sales.html` que usa `SalesView`.
- Generar y aplicar migraciones para `accounts`.
