# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    # Puedes agregar otros campos si lo necesitas más adelante
    # Ejemplo: avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username