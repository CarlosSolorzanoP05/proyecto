# C:\DjangoProject\characters\admin.py

from django.contrib import admin
from import_export.admin import ImportExportModelAdmin # <-- ¡IMPORTA ESTO!
from .models import Warrior, Mage, Enemy, Item # Tus modelos
from .resources import WarriorResource, MageResource, EnemyResource, ItemResource # Tus recursos

# Usa el decorador @admin.register() y hereda de ImportExportModelAdmin
@admin.register(Warrior)
class WarriorAdmin(ImportExportModelAdmin): # <-- Hereda de aquí
    resource_class = WarriorResource # <-- Asigna tu recurso
    list_display = ('name', 'owner', 'health', 'damage')

@admin.register(Mage)
class MageAdmin(ImportExportModelAdmin): # <-- Hereda de aquí
    resource_class = MageResource # <-- Asigna tu recurso
    list_display = ('name', 'owner', 'health', 'magic_damage', 'mana')

@admin.register(Enemy)
class EnemyAdmin(ImportExportModelAdmin): # <-- Hereda de aquí
    resource_class = EnemyResource # <-- Asigna tu recurso
    list_display = ('name', 'health', 'attack')

@admin.register(Item)
class ItemAdmin(ImportExportModelAdmin): # <-- Hereda de aquí
    resource_class = ItemResource # <-- Asigna tu recurso
    list_display = ('name', 'value', 'description')