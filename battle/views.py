# C:\DjangoProject\battle\views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required # Para asegurar que solo usuarios logueados accedan

@login_required # Esto asegura que el usuario debe estar logueado para acceder a esta página
def battle_home(request):
    """
    Vista para la página principal de la aplicación de batalla.
    """
    return render(request, 'battle/battle_home.html')

# Puedes añadir más vistas para tu lógica de batalla aquí