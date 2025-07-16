# characters/forms.py
from django import forms
from .models import Warrior, Mage, Enemy, Item

class WarriorForm(forms.ModelForm):
    class Meta:
        model = Warrior
        fields = ['name', 'health', 'defense', 'damage']
        # El 'owner' se asignará automáticamente en la vista

class MageForm(forms.ModelForm):
    class Meta:
        model = Mage
        fields = ['name', 'health', 'defense', 'magic_damage', 'mana']
        # El 'owner' se asignará automáticamente en la vista

class EnemyForm(forms.ModelForm):
    class Meta:
        model = Enemy
        fields = ['name', 'health', 'attack', 'defense']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'item_type', 'damage_buff', 'health_restore', 'mana_restore']