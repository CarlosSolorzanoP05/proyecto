# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'is_admin') # Puedes quitar 'is_admin' si no quieres que se vea en el registro público

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nombre de Usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'password')