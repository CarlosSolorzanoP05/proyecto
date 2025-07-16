# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, LoginForm

# Vista para el registro de usuarios
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login') # Redirige al login después de un registro exitoso
    template_name = 'users/register.html' # Asegúrate de que esta plantilla exista en templates/users/register.html

# Vista para el inicio de sesión
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home') # Redirige a la página 'home' (que ya tienes configurada)
            else:
                form.add_error(None, "Nombre de usuario o contraseña incorrectos.")
    else:
        form = LoginForm()
    # Esta vista renderiza 'users/login.html'. Asegúrate de que este archivo exista.
    return render(request, 'users/../DjangoProject/templates/registration/login.html', {'form': form})

# Vista para cerrar sesión
@login_required
def user_logout(request):
    logout(request)
    return redirect('login') # Redirige al login después de cerrar sesión

# Vista de ejemplo para la página de inicio (después de iniciar sesión)
@login_required
def home_view(request):
    # Esta vista renderiza 'home.html'. Asegúrate de que este archivo exista en la raíz de tus templates.
    return render(request, 'home.html')