# Clase: Crear los modelos usando Django ORM en VSCode

## Temas cubiertos en la clase

- Crear modelos de usuario con campos personalizados.
- Implementar métodos para gestionar usuarios.
- Definir campos y configuraciones para los modelos.

## Contexto

Esta clase agrega una nueva app de Django, `accounts` (`src/accounts/`), pensada
para reemplazar el modelo de usuario por defecto de Django (`django.contrib.auth.models.User`)
por uno personalizado que usa **email en vez de username** para autenticar.

Archivos creados en esta app:

```
src/accounts/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
└── views.py
```

De todos ellos, el archivo con contenido relevante para la clase es
[`models.py`](../../src/accounts/models.py). El resto (`admin.py`, `views.py`,
`tests.py`) todavía están en su estado por defecto, generados por
`python manage.py startapp accounts`.

## Qué se hizo en `models.py`

### 1. Un manager de usuario personalizado (`UserManager`)

Django exige que todo modelo de usuario tenga un *manager* que sepa cómo crear
usuarios. Como este modelo no usa `username`, no se puede reutilizar el manager
por defecto (`UserManager` de `django.contrib.auth`), así que se define uno propio
heredando de `BaseUserManager`:

```python
class UserManager(BaseUserManager):
    def create_user(self, email, full_name=None, password=None, ...):
        ...
    def create_staffuser(self, email, full_name=None, password=None):
        ...
    def create_superuser(self, email, full_name=None, password=None):
        ...
```

- **`create_user`**: método base. Valida que `email` y `password` no estén vacíos,
  normaliza el email (`self.normalize_email`), crea la instancia del modelo,
  hashea la contraseña con `set_password` (nunca se guarda en texto plano) y
  guarda el objeto con `save(using=self._db)` (soporta múltiples bases de datos).
- **`create_staffuser`**: atajo que llama a `create_user` con `is_staff=True`,
  para crear usuarios del panel de administración sin todos los permisos.
- **`create_superuser`**: atajo que llama a `create_user` con `is_staff=True` e
  `is_admin=True`, para crear superusuarios (usado por
  `python manage.py createsuperuser`).

Este patrón (manager con `create_user` / `create_superuser`) es el que Django
espera encontrar en `AUTH_USER_MODEL.objects` para que los comandos de gestión
y el panel de admin funcionen correctamente.

### 2. El modelo `User` con campos personalizados

```python
class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)   # puede iniciar sesión
    staff = models.BooleanField(default=False)   # usuario staff, no superusuario
    admin = models.BooleanField(default=False)   # superusuario
    timestamp = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()
```

Se hereda de `AbstractBaseUser` (no de `AbstractUser`) porque se quiere control
total sobre los campos: **no** se heredan `username`, `first_name`, `last_name`,
`is_staff`, `is_active`, etc. de Django, sino que se definen los propios.

Campos definidos:

| Campo        | Tipo             | Propósito                                              |
|--------------|------------------|----------------------------------------------------------|
| `email`      | `EmailField`     | Identificador único de login (reemplaza a `username`).   |
| `full_name`  | `CharField`      | Nombre completo, opcional (`blank=True, null=True`).      |
| `active`     | `BooleanField`   | Si el usuario puede iniciar sesión.                       |
| `staff`      | `BooleanField`   | Si el usuario puede entrar al panel de admin.              |
| `admin`      | `BooleanField`   | Si el usuario tiene todos los permisos (superusuario).      |
| `timestamp`  | `DateTimeField`  | Fecha de creación (`auto_now_add=True`, se fija una sola vez). |

Configuraciones clave para que Django trate este modelo como el modelo de
autenticación:

- `USERNAME_FIELD = 'email'`: le indica a Django que el login se hace por email
  en vez de por username.
- `REQUIRED_FIELDS = []`: campos adicionales que pide `createsuperuser` además
  del `USERNAME_FIELD` y la contraseña (aquí no se pide ninguno más).
- `objects = UserManager()`: conecta el modelo con el manager personalizado
  del paso anterior.

## Estado actual del código (pendiente de completar)

Al momento de esta clase, `models.py` quedó **incompleto** y con un par de
detalles a corregir en la siguiente sesión:

1. **Import roto**: `from django.core.urlsrolvers import reverse` tiene un typo
   (`urlsrolvers`) y además ese módulo no existe en versiones modernas de
   Django (fue reemplazado por `django.urls` hace varias versiones). Este
   proyecto usa Django 6.0, así que habría que cambiarlo a
   `from django.urls import reverse` o quitarlo si no se usa.
2. **Métodos requeridos por `AbstractBaseUser` / Django admin** todavía no están
   implementados. Para que el modelo funcione con `django.contrib.auth` y con
   el panel de administración falta agregar, entre otros:
   - `__str__` (representación del usuario).
   - Propiedades `is_staff`, `is_active`, `is_admin` (Django las usa
     internamente; hoy el modelo solo tiene los campos `staff`, `active`,
     `admin` "planos").
   - `get_full_name()` / `get_short_name()`.
   - `has_perm(self, perm, obj=None)` y `has_module_perms(self, app_label)`.
3. **Imports sin usar todavía**: `timedelta`, `Q`, `pre_save`, `post_save`,
   `send_mail`, `render_to_string`, y la constante `DEFAULT_ACTIVATION_DAYS`
   están importados/definidos pero no se usan aún — quedaron preparados para
   una clase futura (probablemente activación de cuenta por email).
4. **La app todavía no está registrada** en `INSTALLED_APPS`
   ([`src/config/settings.py`](../../src/config/settings.py)) ni se configuró
   `AUTH_USER_MODEL = "accounts.User"`, así que Django todavía no usa este
   modelo como el modelo de usuario activo.
5. No se han generado las migraciones (`python manage.py makemigrations accounts`).

## Próximos pasos sugeridos

- Corregir el import de `reverse`.
- Completar los métodos y propiedades que pide `AbstractBaseUser`.
- Registrar `accounts` en `INSTALLED_APPS` y definir `AUTH_USER_MODEL`.
- Registrar el modelo en `admin.py` para poder gestionarlo desde el panel.
- Generar y aplicar las migraciones.
