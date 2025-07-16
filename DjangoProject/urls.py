# DjangoProject/urls.py

from django.contrib import admin
from django.urls import path, include
from users.views import home_view # Importa la vista home_view de tu aplicación 'users'
from django.contrib.auth import views as auth_views # Importar las vistas de autenticación de Django

urlpatterns = [
    # Panel de administración de Django
    path('admin/', admin.site.urls),

    # URLs de autenticación de Django PERSONALIZADAS para usar tus plantillas
    # Login: usa la LoginView de Django y le indica que use 'registration/login.html'
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Logout: usa la LogoutView de Django y redirige a la página de login después de cerrar sesión
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Incluir el resto de las URLs de autenticación de Django (restablecimiento de contraseña, etc.)
    # Las rutas definidas arriba tienen precedencia sobre las que puedan solaparse aquí.
    path('accounts/', include('django.contrib.auth.urls')),

    # URLs para las funcionalidades de registro y gestión de usuarios (de tu app 'users')
    path('accounts/signup/', include('users.urls', namespace='users')),

    # URL para la página de inicio (home_view)
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),

    # Incluye las URLs de tu aplicación 'characters'
    # ¡Asegúrate de que 'characters/urls.py' tenga 'app_name = "characters"'!
    path('characters/', include('characters.urls', namespace='characters')),

    # Incluye las URLs de tu aplicación 'battle'
    # ¡Asegúrate de que 'battle/urls.py' tenga 'app_name = "battle"'!
    path('battle/', include('battle.urls', namespace='battle')),
]