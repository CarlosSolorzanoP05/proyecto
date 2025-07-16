# battle/urls.py

from django.urls import path
from . import views
app_name = 'battle'
urlpatterns = [
    # Ejemplo de ruta de prueba
    path('', views.battle_home, name='battle_home'),
]
