# characters/models.py
from django.core.validators import RegexValidator, MinValueValidator
from django.conf import settings # Para acceder al modelo de usuario personalizado
from django.db import models
from django.db.models import JSONField

# Validador para nombres (solo letras y espacios)
alphabetic_validator = RegexValidator(
    # Actualizado para incluir caracteres especiales del español y otros permitidos en nombres
    r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\'-]+$',
    'El nombre solo puede contener letras, espacios, guiones y apóstrofes.'
)
class Character(models.Model):
    """Clase base abstracta para personajes."""
    # Eliminamos el campo owner de aquí, ya que lo definiremos en las subclases.
    name = models.CharField(max_length=100, unique=True, validators=[alphabetic_validator])
    health = models.IntegerField(default=100, validators=[MinValueValidator(0)])
    defense = models.IntegerField(default=10, validators=[MinValueValidator(0)])

    class Meta:
        abstract = True # Esto indica que es una clase base abstracta y no creará una tabla en la DB
        ordering = ['name']

    def __str__(self):
        return self.name

class Warrior(Character):
    """Personaje tipo Guerrero."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='warriors')
    damage = models.IntegerField(default=20, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Guerrero: {self.name}"

class Mage(Character):
    """Personaje tipo Mago."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mages')
    magic_damage = models.IntegerField(default=25, validators=[MinValueValidator(0)])
    mana = models.IntegerField(default=50, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"Mago: {self.name}"

class Enemy(models.Model):
    """Personaje tipo Enemigo."""
    name = models.CharField(max_length=100, unique=True, validators=[alphabetic_validator])
    health = models.IntegerField(default=50, validators=[MinValueValidator(0)])
    attack = models.IntegerField(default=15, validators=[MinValueValidator(0)])
    defense = models.IntegerField(default=5, validators=[MinValueValidator(0)])

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"Enemigo: {self.name}"

class Item(models.Model):
    """Modelo para los ítems."""
    ITEM_TYPES = (
        ('SWORD', 'Espada (Guerrero)'),
        ('STAFF', 'Bastón (Mago)'),
        ('HEALTH_POTION', 'Poción de Vida'),
        ('MANA_POTION', 'Poción de Maná'),
    )
    name = models.CharField(max_length=100, unique=True)
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES)
    # --- Fields from the second definition, now merged ---
    description = models.TextField(blank=True, null=True) # Added blank=True, null=True for flexibility
    value = models.IntegerField(default=0, validators=[MinValueValidator(0)]) # Added validator
    extra_attributes = JSONField(default=dict, blank=True, null=True)
    # --- End merged fields ---
    damage_buff = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)],
                                      help_text="Daño adicional si es espada/bastón.")
    health_restore = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)],
                                         help_text="Cantidad de vida que cura si es poción de vida.")
    mana_restore = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)],
                                       help_text="Cantidad de maná que restaura si es poción de maná.")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name