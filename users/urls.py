# users/urls.py

from django.urls import path
from . import views # Esta línea DEBE ESTAR

app_name = 'users' # Esta línea DEBE ESTAR

urlpatterns = [
    # Esta es la única URL que debe ir aquí para tu registro personalizado
    path('register/', views.RegisterView.as_view(), name='register'),
]

# NO debe haber ninguna otra línea de 'path' aquí, especialmente ninguna que use 'include()'
# Asegúrate de que las líneas de 'login', 'logout', y 'home' también hayan sido ELIMINADAS si las tenías.
# Es decir, no debe haber:
# path('login/', views.user_login, name='login'),
# path('logout/', views.user_logout, name='logout'),
# path('home/', views.home_view, name='home'),
# Y DEFINITIVAMENTE NO DEBE HABER:
# path('accounts/signup/', include('users.urls', namespace='users')),