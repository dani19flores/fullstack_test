"""
URL configuration for hello project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("up/", include("up.urls")),
    path("api/token/", obtain_auth_token, name="api-token-auth"),
    path("api/token/jwt/", TokenObtainPairView.as_view(), name="jwt-obtain"),
    path("api/token/jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("api/token/jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path("", include("pages.urls")),
    path("analytics/", include("analytics.urls")),
    path("ventas/", include("ventas.urls")),
    path("admin/", admin.site.urls),
    path("forms/", include("forms_test.urls")),
    path("test_templates/", include("test_templates.urls")),
    path("templates-demo/", include("templates_demo.urls")),
    path("api/v1/", include("api.urls")),
    path("api/v2/", include("rest_examples.urls")),
    path("api/products/", include("products.urls")),
    path("accounts/", include("user_apps.urls")),
    path("billing/", include("billing.urls")),
    path("addresses/", include("addresses.urls")),
    path("order/", include("order.urls")),
    path("newsletter/", include("accounts.urls")),
]
if not settings.TESTING:
    urlpatterns = [
        *urlpatterns,
        path("__debug__/", include("debug_toolbar.urls")),
    ]
