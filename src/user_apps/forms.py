from django import forms
from django.contrib.auth.forms import AuthenticationForm

INPUT_CLASSES = (
    "block w-full rounded-md border border-gray-300 px-3 py-2 text-sm "
    "text-gray-900 placeholder:text-gray-400 focus:border-gray-500 "
    "focus:outline-none focus:ring-1 focus:ring-gray-500"
)


class StyledAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "autofocus": True, "placeholder": "Usuario"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": INPUT_CLASSES, "placeholder": "Contraseña"})
    )
